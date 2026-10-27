from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.tago import TagoClient
from app.core.errors import ExternalServiceError, ValidationError
from app.core.settings import settings
from app.db.session import get_db
from app.models.bus_city_code import BusCityCode
from app.models.bus_realtime_arrival import BusRealtimeArrival
from app.models.raw_public_data import RawPublicData
from app.schemas.transit import BusArrivalItem, BusArrivalResponse, CityCodeItem


def _item(row: dict, city_code: str) -> BusArrivalItem:
    return BusArrivalItem(
        node_id=str(row.get("nodeid") or row.get("nodeId")),
        node_name=row.get("nodenm") or row.get("nodeNm"),
        route_id=str(row.get("routeid") or row.get("routeId")),
        route_no=str(row.get("routeno") or row.get("routeNo") or ""),
        route_type=row.get("routetp") or row.get("routeTp"),
        arr_prev_station_cnt=_to_int(row.get("arrprevstationcnt")),
        vehicle_type=row.get("vehicletp") or row.get("vehicleTp"),
        arr_time_seconds=_to_int(row.get("arrtime")),
        city_code=city_code,
    )


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class BusService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def list_cities(self, refresh: bool = False) -> list[CityCodeItem]:
        if not refresh:
            existing = (await self.db.execute(select(BusCityCode).order_by(BusCityCode.city_code))).scalars().all()
            if existing:
                return [CityCodeItem(city_code=r.city_code, city_name=r.city_name) for r in existing]

        client = TagoClient()
        try:
            raw = await client.get_city_codes()
        finally:
            await client.aclose()

        raw_row = await self._save_raw("tago_bus", "getCtyCodeList", raw)
        now = datetime.now(timezone.utc)
        cities: list[CityCodeItem] = []
        for item in raw["items"]:
            code = str(item.get("citycode") or item.get("cityCode"))
            name = str(item.get("cityname") or item.get("cityName") or "")
            if not code:
                continue
            row = await self.db.get(BusCityCode, code)
            if row:
                row.city_name = name
                row.updated_at = now
            else:
                self.db.add(BusCityCode(city_code=code, city_name=name, fetched_at=now, updated_at=now))
            cities.append(CityCodeItem(city_code=code, city_name=name))
        raw_row.parsed_at = now
        raw_row.record_count = len(cities)
        await self.db.commit()
        return cities

    async def arrivals(
        self,
        *,
        city_code: str,
        node_id: str,
        route_id: str | None = None,
        num_of_rows: int = 10,
        page_no: int = 1,
    ) -> BusArrivalResponse:
        if not city_code or not node_id:
            raise ValidationError("cityCode and nodeId are required")

        service = (
            "getSttnAcctoSpcifyRouteBusArvlPrearngeInfoList"
            if route_id
            else "getSttnAcctoArvlPrearngeInfoList"
        )
        client = TagoClient()
        try:
            if route_id:
                raw = await client.get_route_arrivals(
                    city_code=city_code, node_id=node_id, route_id=route_id,
                    num_of_rows=num_of_rows, page_no=page_no,
                )
            else:
                raw = await client.get_stop_arrivals(
                    city_code=city_code, node_id=node_id,
                    num_of_rows=num_of_rows, page_no=page_no,
                )
        except (ExternalServiceError, ValidationError):
            cached = await self._cached_arrivals(city_code, node_id, route_id)
            if cached:
                return cached
            raise
        finally:
            await client.aclose()

        fetched_at = datetime.now(timezone.utc)
        items = [_item(row, city_code) for row in raw["items"] if row.get("nodeid") or row.get("nodeId")]
        try:
            raw_row = await self._save_raw("tago_bus", service, raw, {
                "cityCode": city_code, "nodeId": node_id, "routeId": route_id,
                "numOfRows": num_of_rows, "pageNo": page_no,
            })
            for item in items:
                self.db.add(BusRealtimeArrival(
                    fetched_at=fetched_at,
                    city_code=item.city_code,
                    node_id=item.node_id,
                    node_name=item.node_name,
                    route_id=item.route_id,
                    route_no=item.route_no,
                    route_type=item.route_type,
                    arr_prev_station_cnt=item.arr_prev_station_cnt,
                    vehicle_type=item.vehicle_type,
                    arr_time_seconds=item.arr_time_seconds,
                    service=service,
                    raw_id=raw_row.id,
                ))
            raw_row.parsed_at = fetched_at
            raw_row.record_count = len(items)
            await self.db.commit()
        except Exception:
            await self.db.rollback()

        return BusArrivalResponse(
            city_code=city_code,
            node_id=node_id,
            route_id=route_id,
            fetched_at=fetched_at,
            last_fetched_at=fetched_at,
            result_code=raw["result_code"],
            result_message=raw["result_msg"],
            total_count=int(raw.get("total_count") or len(items)),
            items=items,
            realtime=True,
        )

    async def _cached_arrivals(
        self, city_code: str, node_id: str, route_id: str | None
    ) -> BusArrivalResponse | None:
        stmt = select(BusRealtimeArrival).where(
            BusRealtimeArrival.city_code == city_code,
            BusRealtimeArrival.node_id == node_id,
        )
        if route_id:
            stmt = stmt.where(BusRealtimeArrival.route_id == route_id)
        stmt = stmt.order_by(BusRealtimeArrival.fetched_at.desc()).limit(50)
        rows = (await self.db.execute(stmt)).scalars().all()
        if not rows:
            return None
        latest = rows[0].fetched_at
        batch = [r for r in rows if r.fetched_at == latest]
        stale = (datetime.now(timezone.utc) - latest).total_seconds() > settings.REALTIME_STALE_SECONDS
        items = [
            BusArrivalItem(
                node_id=r.node_id,
                node_name=r.node_name,
                route_id=r.route_id,
                route_no=r.route_no,
                route_type=r.route_type,
                arr_prev_station_cnt=r.arr_prev_station_cnt,
                vehicle_type=r.vehicle_type,
                arr_time_seconds=r.arr_time_seconds,
                city_code=r.city_code,
                stale=stale,
            )
            for r in batch
        ]
        return BusArrivalResponse(
            city_code=city_code,
            node_id=node_id,
            route_id=route_id,
            fetched_at=latest,
            last_fetched_at=latest,
            result_code="CACHE",
            result_message="실시간 정보 미반영",
            total_count=len(items),
            items=items,
            realtime=False,
        )

    async def _save_raw(self, source: str, service: str, raw: dict, params: dict | None = None) -> RawPublicData:
        row = RawPublicData(
            source=source,
            service=service,
            request_url=raw.get("url"),
            request_params=params,
            http_status=raw.get("http_status"),
            content_type=raw.get("content_type"),
            body=raw.get("body"),
            result_code=raw.get("result_code"),
            result_message=raw.get("result_msg") or raw.get("result_message"),
            record_count=len(raw.get("items") or []),
        )
        self.db.add(row)
        await self.db.flush()
        return row
