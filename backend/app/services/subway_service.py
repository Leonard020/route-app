from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.seoul_subway import (
    ARRIVAL_CODE_MAP,
    SUBWAY_LINE_MAP,
    SeoulSubwayClient,
    parse_ordkey,
    parse_recptn_dt,
    parse_updn,
    split_csv,
)
from app.core.errors import ExternalServiceError, ValidationError
from app.core.settings import settings
from app.db.session import get_db
from app.models.data_sync_log import DataSyncLog
from app.models.raw_public_data import RawPublicData
from app.models.subway_line import SubwayLine
from app.models.subway_realtime_arrival import SubwayRealtimeArrival
from app.models.subway_station import SubwayStation
from app.models.subway_station_transfer import SubwayStationTransfer
from app.schemas.transit import SubwayArrivalItem, SubwayArrivalResponse


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_item(row: dict) -> SubwayArrivalItem:
    subway_id = str(row.get("subwayId") or "")
    arrival_code = _to_int(row.get("arvlCd"))
    return SubwayArrivalItem(
        subway_id=subway_id,
        line_name=SUBWAY_LINE_MAP.get(subway_id),
        station_id=str(row.get("statnId") or ""),
        station_name=row.get("statnNm"),
        updn_line=parse_updn(row.get("updnLine")),
        train_line_nm=row.get("trainLineNm"),
        prev_station_id=row.get("statnFid"),
        next_station_id=row.get("statnTid"),
        transfer_count=_to_int(row.get("trnsitCo")) or 0,
        ord_key=row.get("ordkey"),
        train_type=row.get("btrainSttus"),
        arrival_seconds=_to_int(row.get("barvlDt")),
        train_no=row.get("btrainNo"),
        final_station_id=row.get("bstatnId"),
        final_station_name=row.get("bstatnNm"),
        recptn_dt=parse_recptn_dt(row.get("recptnDt")),
        first_msg=row.get("arvlMsg2"),
        second_msg=row.get("arvlMsg3"),
        arrival_code=arrival_code,
        arrival_code_name=ARRIVAL_CODE_MAP.get(arrival_code) if arrival_code is not None else None,
        is_last_car=str(row.get("lstcarAt") or "0") in ("1", "true", "True"),
        transfer_line_ids=split_csv(row.get("subwayList")),
        transfer_station_ids=split_csv(row.get("statnList")),
    )


class SubwayService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def arrivals(
        self,
        *,
        station_name: str | None = None,
        subway_id: str | None = None,
        station_id: str | None = None,
        updn_line: int | None = None,
        start_index: int = 1,
        end_index: int | None = None,
        persist: bool = True,
    ) -> SubwayArrivalResponse:
        end_index = end_index or min(start_index + settings.SEOUL_SUBWAY_PAGE_SIZE - 1, start_index + 999)
        client = SeoulSubwayClient()
        try:
            raw = await client.get_all(start_index, end_index)
        except (ExternalServiceError, ValidationError):
            cached = await self._cached_arrivals(station_name, subway_id, station_id, updn_line)
            if cached:
                return cached
            raise
        finally:
            await client.aclose()

        fetched_at = datetime.now(timezone.utc)
        items = [_to_item(row) for row in raw["items"]]
        if station_name:
            items = [i for i in items if (i.station_name or "") == station_name]
        if subway_id:
            items = [i for i in items if i.subway_id == subway_id]
        if station_id:
            items = [i for i in items if i.station_id == station_id]
        if updn_line is not None:
            items = [i for i in items if i.updn_line == updn_line]

        raw_row = None
        if persist:
            raw_row = RawPublicData(
                source="seoul_subway",
                service="realtimeStationArrival/ALL",
                request_url=raw.get("url"),
                request_params={"START_INDEX": start_index, "END_INDEX": end_index},
                http_status=raw.get("http_status"),
                content_type=raw.get("content_type"),
                body=raw.get("body"),
                result_code=raw.get("result_code"),
                result_message=raw.get("result_message"),
                record_count=raw.get("record_count"),
                parsed_at=fetched_at,
            )
            self.db.add(raw_row)
            await self.db.flush()
            await self._persist_items(raw["items"], raw_row.id, fetched_at)
            await self.db.commit()

        last_dt = max((i.recptn_dt for i in items if i.recptn_dt), default=fetched_at)
        return SubwayArrivalResponse(
            fetched_at=fetched_at,
            result_code=raw["result_code"],
            result_message=raw["result_message"],
            total_count=len(items),
            items=items,
            realtime=True,
            last_fetched_at=last_dt,
        )

    async def sync_all(self) -> dict:
        started = datetime.now(timezone.utc)
        log = DataSyncLog(
            source="seoul_subway",
            service="realtimeStationArrival/ALL",
            started_at=started,
            status="partial",
        )
        self.db.add(log)
        await self.db.flush()

        fetched = 0
        saved = 0
        start = 1
        page = settings.SEOUL_SUBWAY_PAGE_SIZE
        if settings.SEOUL_SUBWAY_KEY == "sample":
            page = 5
        try:
            while True:
                end = start + page - 1
                result = await self.arrivals(start_index=start, end_index=end, persist=True)
                fetched += result.total_count
                saved += result.total_count
                if result.total_count < page:
                    break
                start = end + 1
            log.status = "success"
        except Exception as exc:
            log.status = "failed"
            log.error_message = str(exc)
            raise
        finally:
            log.finished_at = datetime.now(timezone.utc)
            log.items_fetched = fetched
            log.items_saved = saved
            await self.db.commit()
        return {
            "status": log.status,
            "items_fetched": fetched,
            "items_saved": saved,
            "started_at": started,
            "finished_at": log.finished_at,
        }

    async def _persist_items(self, rows: list[dict], raw_id, fetched_at: datetime) -> None:
        for row in rows:
            item = _to_item(row)
            if not item.station_id:
                continue
            parsed = parse_ordkey(item.ord_key)
            exists = await self.db.scalar(
                select(SubwayStation.id).where(SubwayStation.station_id == item.station_id)
            )
            if not exists:
                self.db.add(SubwayStation(
                    station_id=item.station_id,
                    subway_id=item.subway_id,
                    line_name=item.line_name,
                    station_code=item.station_id[-4:] if len(item.station_id) >= 4 else item.station_id,
                    station_name=item.station_name or item.station_id,
                    station_name_norm=(item.station_name or "").replace(" ", ""),
                    prev_station_id=item.prev_station_id,
                    next_station_id=item.next_station_id,
                    transfer_count=item.transfer_count,
                    is_transfer=item.transfer_count > 0,
                ))
            for line_id, st_id in zip(item.transfer_line_ids, item.transfer_station_ids):
                stmt = insert(SubwayStationTransfer).values(
                    station_id=item.station_id,
                    transfer_subway_id=line_id,
                    transfer_station_id=st_id,
                ).on_conflict_do_nothing(index_elements=["station_id", "transfer_station_id"])
                await self.db.execute(stmt)

            self.db.add(SubwayRealtimeArrival(
                recptn_dt=item.recptn_dt or fetched_at,
                fetched_at=fetched_at,
                subway_id=item.subway_id,
                station_id=item.station_id,
                station_name=item.station_name,
                updn_line=item.updn_line,
                train_line_nm=item.train_line_nm,
                prev_station_id=item.prev_station_id,
                next_station_id=item.next_station_id,
                transfer_count=item.transfer_count,
                ord_key=item.ord_key,
                ord_updn=parsed.get("ord_updn"),
                ord_seq=parsed.get("ord_seq"),
                ord_remaining_stops=parsed.get("ord_remaining_stops"),
                ord_dest_code=parsed.get("ord_dest_code"),
                ord_express=parsed.get("ord_express"),
                transfer_line_ids=item.transfer_line_ids or None,
                transfer_station_ids=item.transfer_station_ids or None,
                train_type=item.train_type,
                arrival_seconds=item.arrival_seconds,
                train_no=item.train_no,
                final_station_id=item.final_station_id,
                final_station_name=item.final_station_name,
                first_msg=item.first_msg,
                second_msg=item.second_msg,
                arrival_code=item.arrival_code,
                is_last_car=item.is_last_car,
                raw_id=raw_id,
            ))

    async def list_lines(self) -> list[dict]:
        rows = (await self.db.execute(select(SubwayLine).order_by(SubwayLine.display_order))).scalars().all()
        return [{"subway_id": r.subway_id, "line_name": r.line_name} for r in rows]

    async def _cached_arrivals(
        self,
        station_name: str | None,
        subway_id: str | None,
        station_id: str | None,
        updn_line: int | None,
    ) -> SubwayArrivalResponse | None:
        stmt = select(SubwayRealtimeArrival)
        if station_name:
            stmt = stmt.where(SubwayRealtimeArrival.station_name == station_name)
        if subway_id:
            stmt = stmt.where(SubwayRealtimeArrival.subway_id == subway_id)
        if station_id:
            stmt = stmt.where(SubwayRealtimeArrival.station_id == station_id)
        if updn_line is not None:
            stmt = stmt.where(SubwayRealtimeArrival.updn_line == updn_line)
        stmt = stmt.order_by(SubwayRealtimeArrival.fetched_at.desc()).limit(80)
        rows = (await self.db.execute(stmt)).scalars().all()
        if not rows:
            return None
        latest = rows[0].fetched_at
        batch = [r for r in rows if r.fetched_at == latest]
        items = []
        for row in batch:
            items.append(SubwayArrivalItem(
                subway_id=row.subway_id,
                line_name=SUBWAY_LINE_MAP.get(row.subway_id),
                station_id=row.station_id,
                station_name=row.station_name,
                updn_line=row.updn_line,
                train_line_nm=row.train_line_nm,
                prev_station_id=row.prev_station_id,
                next_station_id=row.next_station_id,
                transfer_count=row.transfer_count or 0,
                ord_key=row.ord_key,
                train_type=row.train_type,
                arrival_seconds=row.arrival_seconds,
                train_no=row.train_no,
                final_station_id=row.final_station_id,
                final_station_name=row.final_station_name,
                recptn_dt=row.recptn_dt,
                first_msg=row.first_msg,
                second_msg=row.second_msg,
                arrival_code=row.arrival_code,
                arrival_code_name=ARRIVAL_CODE_MAP.get(row.arrival_code) if row.arrival_code is not None else None,
                is_last_car=row.is_last_car,
                transfer_line_ids=row.transfer_line_ids or [],
                transfer_station_ids=row.transfer_station_ids or [],
            ))
        return SubwayArrivalResponse(
            fetched_at=latest,
            result_code="CACHE",
            result_message="실시간 정보 미반영",
            total_count=len(items),
            items=items,
            realtime=False,
            last_fetched_at=latest,
        )
