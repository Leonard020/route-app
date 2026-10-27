from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bus_hourly_boarding import BusHourlyBoarding
from app.models.station_transfer_flow import StationTransferFlow
from app.models.subway_station_transfer import SubwayStationTransfer


def _congestion(board: int, alight: int) -> int:
    load = board + alight
    if load >= 1200:
        return 5
    if load >= 700:
        return 4
    if load >= 350:
        return 3
    if load >= 120:
        return 2
    return 1


def _dwell_s(board: int) -> int:
    return min(90, board // 40)


class DemandService:
    """시간대별 승하차·환승시간 통계를 경로 후보에 반영합니다. 데이터가 없으면 기존 휴리스틱을 유지합니다."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_to_candidates(self, candidates: list[dict], hour: int) -> None:
        hour = max(0, min(23, int(hour)))
        try:
            for cand in candidates:
                await self._apply_one(cand, hour)
        except Exception:
            await self.db.rollback()

    async def _apply_one(self, cand: dict, hour: int) -> None:
        steps = cand.get("steps") or []
        segments = cand.get("segments") or []
        prev_alight_id = None
        for i, step in enumerate(steps):
            mode = step.get("mode")
            info = step.get("transit_info") or {}
            if mode == "bus":
                stop_id = (
                    info.get("standard_stop_id")
                    or info.get("node_id")
                    or info.get("external_id")
                )
                route_no = info.get("route_no")
                row = await self._bus_row(route_no, stop_id)
                if row:
                    board, alight = row.counts_at(hour)
                    cong = _congestion(board, alight)
                    dwell = _dwell_s(board)
                    step["duration_s"] = int(step.get("duration_s") or 60) + dwell
                    info["demand_boarding"] = board
                    info["demand_alight"] = alight
                    info["demand_hour"] = hour
                    info["demand_source"] = "bus_hourly_boardings"
                    step["transit_info"] = info
                    self._set_segment_congestion(segments, "bus", cong)
                prev_alight_id = info.get("alight_stop_id") or info.get("standard_stop_id") or info.get("node_id")
            elif mode == "subway":
                board_id = info.get("card_stop_id") or info.get("station_id")
                if prev_alight_id and board_id:
                    xfer = await self._transfer_s(prev_alight_id, board_id, hour)
                    if xfer:
                        self._apply_transfer_walk(steps, i, xfer, hour)
                prev_alight_id = info.get("card_stop_id") or info.get("station_id")
            elif mode == "walk" and "환승" in str(step.get("instruction") or ""):
                nxt = steps[i + 1] if i + 1 < len(steps) else {}
                ninfo = nxt.get("transit_info") or {}
                board_id = ninfo.get("card_stop_id") or ninfo.get("station_id") or ninfo.get("node_id")
                if prev_alight_id and board_id:
                    xfer = await self._transfer_s(prev_alight_id, board_id, hour)
                    if xfer:
                        step["duration_s"] = xfer
                        step["instruction"] = f"{step.get('instruction')} (환승통계 {xfer}초)"

    def _set_segment_congestion(self, segments: list, road_type: str, congestion: int) -> None:
        for seg in segments:
            if seg.get("road_type") == road_type:
                seg["congestion"] = max(int(seg.get("congestion") or 1), congestion)

    def _apply_transfer_walk(self, steps: list, subway_index: int, seconds: int, hour: int) -> None:
        if subway_index <= 0:
            return
        walk = steps[subway_index - 1]
        if walk.get("mode") != "walk":
            return
        walk["duration_s"] = seconds
        note = walk.get("instruction") or "환승 도보"
        if "환승통계" not in note:
            walk["instruction"] = f"{note} (환승통계 {seconds}초, {hour}시대)"

    async def _bus_row(self, route_no: str | None, stop_id: str | None) -> BusHourlyBoarding | None:
        if not stop_id:
            return None
        stmt = (
            select(BusHourlyBoarding)
            .where(BusHourlyBoarding.standard_stop_id == str(stop_id))
            .order_by(BusHourlyBoarding.use_ym.desc())
            .limit(8)
        )
        rows = list((await self.db.execute(stmt)).scalars().all())
        if not rows:
            return None
        if route_no:
            for row in rows:
                if str(row.route_no) == str(route_no):
                    return row
        return rows[0]

    async def _transfer_s(self, alight_id: str, board_id: str, hour: int) -> int | None:
        stmt = (
            select(StationTransferFlow)
            .where(
                StationTransferFlow.alight_stop_id == str(alight_id),
                StationTransferFlow.board_stop_id == str(board_id),
                StationTransferFlow.hour == hour,
            )
            .order_by(StationTransferFlow.base_date.desc())
            .limit(1)
        )
        row = (await self.db.execute(stmt)).scalar_one_or_none()
        if row and row.transfer_time_avg_s:
            return int(row.transfer_time_avg_s)
        stmt2 = (
            select(StationTransferFlow)
            .where(
                StationTransferFlow.alight_stop_id == str(alight_id),
                StationTransferFlow.board_stop_id == str(board_id),
            )
            .order_by(StationTransferFlow.base_date.desc())
            .limit(1)
        )
        row = (await self.db.execute(stmt2)).scalar_one_or_none()
        if row and row.transfer_time_avg_s:
            return int(row.transfer_time_avg_s)
        mapped = (
            await self.db.execute(
                select(SubwayStationTransfer).where(
                    SubwayStationTransfer.station_id == str(alight_id),
                    SubwayStationTransfer.transfer_station_id == str(board_id),
                )
            )
        ).scalar_one_or_none()
        if mapped and mapped.avg_transfer_s:
            return int(mapped.avg_transfer_s)
        return None
