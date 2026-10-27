import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID, uuid4
from app.core.errors import NotFoundError, ExternalServiceError, ValidationError
from app.domain import messages
from app.domain.timing import VehicleOption, pick_boardable, pick_transfer, summarize_durations
from app.core.response import Meta
from app.db.session import get_db
from app.deps.predictor import get_predictor
from app.models.feedback import Feedback
from app.ports.predictor import (
    PredictorPort, ETARequest, ETASegmentIn,
    RankRequest, RankCandidate, RankUserContext,
)
from app.repositories.route_repo import RouteRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.feedback_repo import FeedbackRepository
from app.schemas.route import (
    RouteRecommendRequest, RouteRecommendResponse, RouteOut, RouteStep,
    RouteSummary, RerouteRequest, RerouteResponse, RerouteDelta, FeedbackCreate, LatLng,
)
from app.models.route import Route as RouteModel
from app.core.settings import settings
from app.services.bus_service import BusService
from app.services.subway_service import SubwayService
from app.engines.router import Router
from app.engines.graph import GraphProvider
from app.engines.eta import ETAService


class RouteService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        predictor: PredictorPort = Depends(get_predictor),
        graph_provider: GraphProvider = Depends(),
    ):
        self.db = db
        self.predictor = predictor
        self.graph = graph_provider
        self.routes = RouteRepository(db)
        self.predictions = PredictionRepository(db)
        self.feedbacks = FeedbackRepository(db)
        self.router = Router(graph_provider)
        self.eta = ETAService(predictor)

    async def recommend(
        self,
        payload: RouteRecommendRequest,
        user=None,
    ) -> dict:
        t0 = time.perf_counter()
        if (
            abs(payload.origin.lat - payload.destination.lat) < 1e-6
            and abs(payload.origin.lng - payload.destination.lng) < 1e-6
        ):
            raise ValidationError(messages.SAME_ORIGIN_DEST)

        # 1) 후보 경로 탐색
        candidates = await self.router.find_candidates(
            origin=(payload.origin.lat, payload.origin.lng),
            destination=(payload.destination.lat, payload.destination.lng),
            mode=payload.mode,
            top_k=(payload.options.top_n if payload.options else 3) * 2,
            preferences=payload.preferences.model_dump() if payload.preferences else None,
        )
        if not candidates:
            raise NotFoundError(messages.NO_ROUTE)

        realtime_meta = await self._apply_realtime(candidates)

        # 2) ETA 예측 (PredictorPort)
        eta_results = []
        for c in candidates:
            segments = [
                ETASegmentIn(
                    seg_id=f"s{i}",
                    distance_m=s["distance_m"],
                    road_type=s.get("road_type"),
                    hour=datetime.now().hour,
                    weekday=datetime.now().weekday(),
                    congestion=s.get("congestion"),
                )
                for i, s in enumerate(c["segments"])
            ]
            eta_resp = await self.eta.predict(
                request_id=f"req-{t0}",
                route_id=c["candidate_id"],
                segments=segments,
                depart_at=payload.depart_at or datetime.now(timezone.utc),
                mode=payload.mode,
            )
            wait = int(c.get("realtime_wait_s") or 0)
            if wait:
                eta_resp = eta_resp.model_copy(
                    update={"total_duration_s": eta_resp.total_duration_s + wait}
                )
            eta_results.append(eta_resp)
            try:
                await self.predictions.log(
                    route_id=None,
                    predictor_version=eta_resp.model_version,
                    kind="eta",
                    request={"segments": [s.model_dump() for s in segments]},
                    response=eta_resp.model_dump(mode="json"),
                    latency_ms=int((time.perf_counter() - t0) * 1000),
                    fallback_used=eta_resp.fallback,
                )
            except Exception:
                await self.db.rollback()

        # 3) 랭킹 (PredictorPort)
        rank_req = RankRequest(
            request_id=f"rank-{t0}",
            user_context=RankUserContext(
                preferred_mode=payload.preferences.preferred_mode if payload.preferences else None,
                eco_priority=payload.preferences.eco_priority if payload.preferences else False,
                max_walk_min=payload.preferences.max_walk_min if payload.preferences else 20,
                accessibility=payload.preferences.accessibility if payload.preferences else False,
                walk_speed=payload.preferences.walk_speed if payload.preferences else "normal",
                route_sort=payload.preferences.route_sort if payload.preferences else "fastest",
            ),
            candidates=[
                RankCandidate(
                    route_id=c["candidate_id"],
                    mode=payload.mode,
                    duration_s=eta_results[i].total_duration_s,
                    distance_m=c["total_distance_m"],
                    cost=c.get("total_cost", 0),
                    transfer_count=c.get("transfer_count", 0),
                    walk_distance_m=c.get("walk_distance_m", 0),
                    carbon_g=c.get("carbon_g", 0),
                )
                for i, c in enumerate(candidates)
            ],
        )
        rank_resp = await self.predictor.rank_routes(rank_req)

        # 4) 상위 N개 영속화
        top_n = payload.options.top_n if payload.options else 3
        ranked_sorted = sorted(rank_resp.ranked, key=lambda r: r.rank)[:top_n]
        result_routes = []
        for rank_item in ranked_sorted:
            c = next(x for x in candidates if x["candidate_id"] == rank_item.route_id)
            eta = next(e for e in eta_results if e.request_id == rank_item.route_id) \
                if any(e.request_id == rank_item.route_id for e in eta_results) \
                else eta_results[0]

            route_model = RouteModel(
                user_id=user.id if user else None,
                origin_place_id=_as_uuid(payload.origin.place_id),
                dest_place_id=_as_uuid(payload.destination.place_id),
                origin_lat=payload.origin.lat,
                origin_lng=payload.origin.lng,
                dest_lat=payload.destination.lat,
                dest_lng=payload.destination.lng,
                mode=payload.mode,
                preference_snapshot=payload.preferences.model_dump() if payload.preferences else None,
                total_distance_m=c["total_distance_m"],
                total_duration_s=eta.total_duration_s,
                total_cost=c.get("total_cost", 0),
                transfer_count=c.get("transfer_count", 0),
                walk_distance_m=c.get("walk_distance_m", 0),
                carbon_g=c.get("carbon_g", 0),
                eta=datetime.now(timezone.utc) + timedelta(seconds=eta.total_duration_s),
                polyline=c.get("polyline") if (payload.options and payload.options.include_polyline) else None,
                predictor_version=eta.model_version,
            )
            steps_payload = self._to_steps_payload(c.get("steps", []))
            parts = summarize_durations(steps_payload)
            route_model.total_duration_s = parts["total_duration_s"] or eta.total_duration_s
            route_model.eta = datetime.now(timezone.utc) + timedelta(seconds=route_model.total_duration_s)
            try:
                await self.routes.add_with_steps(route_model, steps_payload)
                await self.db.commit()
                route_id = str(route_model.id)
            except Exception:
                await self.db.rollback()
                route_id = str(uuid4())

            result_routes.append(RouteOut(
                route_id=route_id,
                rank=rank_item.rank,
                mode=payload.mode,
                summary=RouteSummary(
                    total_distance_m=route_model.total_distance_m,
                    total_duration_s=route_model.total_duration_s,
                    total_cost=route_model.total_cost,
                    transfer_count=route_model.transfer_count,
                    walk_distance_m=route_model.walk_distance_m,
                    carbon_g=route_model.carbon_g,
                    eta=route_model.eta,
                    realtime_used=realtime_meta.get("used", False),
                    last_fetched_at=realtime_meta.get("fetched_at"),
                    walk_duration_s=parts["walk_duration_s"],
                    wait_duration_s=parts["wait_duration_s"],
                    vehicle_duration_s=parts["vehicle_duration_s"],
                    transfer_walk_s=parts["transfer_walk_s"],
                    transfer_wait_s=parts["transfer_wait_s"],
                    label=messages.FASTEST if rank_item.rank == 1 else None,
                    time_basis=messages.TIMETABLE if not realtime_meta.get("used") else None,
                ),
                polyline=route_model.polyline,
                steps=[RouteStep(**s) for s in steps_payload] if (payload.options and payload.options.include_steps) else [],
                predictor_version=rank_resp.model_version,
                score=rank_item.score,
                reason=rank_item.reason,
            ))

        meta = Meta(
            predictor_fallback=any(e.fallback for e in eta_results) or rank_resp.fallback,
            predictor_version=rank_resp.model_version,
        )
        return {"data": RouteRecommendResponse(routes=result_routes), "meta": meta}

    async def get_detail(self, route_id: str) -> dict:
        route = await self.routes.get_with_steps(route_id)
        if not route:
            raise NotFoundError("route not found")
        return self._serialize_route(route)

    async def refresh(self, route_id: str) -> RerouteResponse:
        route = await self.routes.get_with_steps(route_id)
        if not route:
            raise NotFoundError("route not found")
        return await self.reroute(
            route_id,
            RerouteRequest(
                current_location=LatLng(lat=route.origin_lat, lng=route.origin_lng),
                reason="manual",
            ),
        )

    async def reroute(self, route_id: str, payload: RerouteRequest) -> RerouteResponse:
        route = await self.routes.get_with_steps(route_id)
        if not route:
            raise NotFoundError("route not found")

        # 새 경로 탐색
        rec = await self.recommend(
            RouteRecommendRequest(
                origin=LatLng(lat=payload.current_location.lat, lng=payload.current_location.lng),
                destination=LatLng(lat=route.dest_lat, lng=route.dest_lng),
                mode=route.mode,
            ),
            user=None,
        )
        new_route = rec["data"].routes[0]

        prev_duration = route.total_duration_s
        prev_distance = route.total_distance_m
        delta = RerouteDelta(
            duration_s=new_route.summary.total_duration_s - prev_duration,
            distance_m=new_route.summary.total_distance_m - prev_distance,
            cost=new_route.summary.total_cost - route.total_cost,
        )

        # 기존 경로 상태 갱신
        route.status = "rerouted"
        await self.db.commit()

        return RerouteResponse(
            route_id=route_id,
            changed=True,
            delta=delta,
            route=new_route,
            reason_text=self._reason_text(payload.reason),
        )

    async def feedback(self, route_id: str, payload: FeedbackCreate, user=None) -> dict:
        fb = Feedback(
            user_id=user.id if user else None,
            route_id=route_id,
            type=payload.type,
            rating=payload.rating,
            category=payload.category,
            comment=payload.comment,
        )
        await self.feedbacks.add(fb)
        await self.db.commit()
        return {"feedback_id": str(fb.id)}

    # ---------- helpers ----------
    def _to_steps_payload(self, steps: list[dict]) -> list[dict]:
        out = []
        for i, s in enumerate(steps, start=1):
            out.append({
                "step_order": i,
                "mode": s["mode"],
                "instruction": s.get("instruction"),
                "distance_m": s["distance_m"],
                "duration_s": s["duration_s"],
                "start_lat": s["start"]["lat"],
                "start_lng": s["start"]["lng"],
                "end_lat": s["end"]["lat"],
                "end_lng": s["end"]["lng"],
                "polyline": s.get("polyline"),
                "transit_info": s.get("transit_info"),
                "segments": s.get("segments", []),
            })
        return out

    async def _apply_realtime(self, candidates: list[dict]) -> dict:
        used = False
        fetched_at = None
        bus_svc = BusService(self.db)
        subway_svc = SubwayService(self.db)
        buffer = settings.BOARDING_BUFFER_SECONDS
        for cand in candidates:
            extra_wait = 0
            elapsed = 0
            first_transit = True
            steps = cand.get("steps", [])
            for i, step in enumerate(steps):
                info = step.get("transit_info") or {}
                mode = step.get("mode")
                prev_walk = int(steps[i - 1].get("duration_s") or 0) if i and steps[i - 1].get("mode") == "walk" else 0
                if mode in ("bus", "subway"):
                    vehicles, fetched, live = await self._load_vehicles(mode, info, bus_svc, subway_svc)
                    if fetched:
                        fetched_at = fetched
                    decision = (
                        pick_boardable(vehicles, prev_walk, buffer)
                        if first_transit
                        else pick_transfer(vehicles, elapsed, prev_walk, buffer)
                    )
                    wait = getattr(decision, "wait_seconds", None)
                    ok = getattr(decision, "boardable", None)
                    if ok is None:
                        ok = decision.connected
                    if ok and wait is not None:
                        extra_wait += wait
                        step["duration_s"] = int(step.get("duration_s") or 0) + wait
                        info["wait_seconds"] = wait
                        info["boardable"] = True
                        info["realtime"] = live
                        info["fallback"] = None if live else "timetable"
                        if getattr(decision, "risk", False):
                            info["transfer_risk"] = True
                            info["warning"] = messages.TRANSFER_RISK
                        if decision.vehicle:
                            info.update(decision.vehicle.meta)
                        used = used or live
                        first_transit = False
                    else:
                        info["boardable"] = False
                        info["realtime"] = live
                        info["fallback"] = "timetable" if vehicles else "unavailable"
                        info["reason"] = decision.reason
                    step["transit_info"] = info
                elapsed += int(step.get("duration_s") or 0)
            cand["realtime_wait_s"] = extra_wait
            cand["time_parts"] = summarize_durations(steps)
        return {"used": used, "fetched_at": fetched_at}

    async def _load_vehicles(self, mode: str, info: dict, bus_svc, subway_svc):
        vehicles: list[VehicleOption] = []
        fetched_at = None
        live = False
        try:
            if mode == "bus" and info.get("node_id"):
                result = await bus_svc.arrivals(
                    city_code=str(info.get("city_code") or settings.DEFAULT_BUS_CITY_CODE),
                    node_id=str(info["node_id"]),
                    route_id=info.get("route_id"),
                )
                fetched_at = result.fetched_at
                live = result.realtime
                for item in result.items:
                    if item.arr_time_seconds is None:
                        continue
                    vehicles.append(VehicleOption(
                        item.arr_time_seconds,
                        {
                            "arr_time_seconds": item.arr_time_seconds,
                            "route_no": item.route_no,
                            "route_id": item.route_id,
                            "vehicle_type": item.vehicle_type,
                            "arr_prev_station_cnt": item.arr_prev_station_cnt,
                            "last_fetched_at": result.last_fetched_at or result.fetched_at,
                        },
                    ))
            elif mode == "subway" and (info.get("station_name") or info.get("station_id")):
                result = await subway_svc.arrivals(
                    station_name=info.get("station_name"),
                    subway_id=info.get("subway_id"),
                    station_id=info.get("station_id"),
                    updn_line=info.get("updn_line"),
                )
                fetched_at = result.fetched_at
                live = result.realtime
                for item in result.items:
                    if item.arrival_seconds is None:
                        continue
                    if item.is_last_car:
                        meta_extra = {"is_last_car": True}
                    else:
                        meta_extra = {}
                    vehicles.append(VehicleOption(
                        item.arrival_seconds,
                        {
                            "arrival_seconds": item.arrival_seconds,
                            "train_no": item.train_no,
                            "train_type": item.train_type,
                            "train_line_nm": item.train_line_nm,
                            "arrival_code": item.arrival_code,
                            "arrival_code_name": item.arrival_code_name,
                            "is_last_car": item.is_last_car,
                            "last_fetched_at": result.last_fetched_at or result.fetched_at,
                            **meta_extra,
                        },
                    ))
        except ExternalServiceError:
            return [], fetched_at, False
        return vehicles, fetched_at, live

    def _serialize_route(self, route: RouteModel) -> dict:
        parts = summarize_durations([
            {
                "step_order": s.step_order,
                "mode": s.mode,
                "duration_s": s.duration_s,
                "transit_info": s.transit_info or {},
            }
            for s in route.steps
        ])
        return {
            "route_id": str(route.id),
            "mode": route.mode,
            "summary": {
                **parts,
                "total_distance_m": route.total_distance_m,
                "total_duration_s": route.total_duration_s,
                "total_cost": route.total_cost,
                "transfer_count": route.transfer_count,
                "walk_distance_m": route.walk_distance_m,
                "carbon_g": route.carbon_g,
                "eta": route.eta,
            },
            "steps": [
                {
                    "order": s.step_order,
                    "mode": s.mode,
                    "instruction": s.instruction,
                    "distance_m": s.distance_m,
                    "duration_s": s.duration_s,
                    "start": {"lat": s.start_lat, "lng": s.start_lng},
                    "end": {"lat": s.end_lat, "lng": s.end_lng},
                    "polyline": s.polyline,
                    "transit_info": s.transit_info,
                }
                for s in route.steps
            ],
        }

    def _reason_text(self, reason: str) -> str:
        return {
            "traffic": "정체 구간 우회",
            "incident": "돌발 상황 회피",
            "deviation": "경로 이탈 보정",
            "manual": "사용자 요청",
        }.get(reason, "재탐색")


def _as_uuid(value) -> UUID | None:
    if not value:
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None