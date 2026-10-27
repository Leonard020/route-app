from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ETASegmentIn(BaseModel):
    seg_id: str
    distance_m: int
    road_type: Optional[str] = None
    hour: Optional[int] = None
    weekday: Optional[int] = None
    congestion: Optional[int] = None


class ETARequest(BaseModel):
    request_id: str
    route_id: str
    segments: list[ETASegmentIn]
    depart_at: datetime
    mode: str


class ETAResponse(BaseModel):
    request_id: str
    total_duration_s: int
    model_version: str = "heuristic-v1"
    fallback: bool = True


class RankUserContext(BaseModel):
    preferred_mode: Optional[str] = None
    eco_priority: bool = False
    max_walk_min: int = 20
    accessibility: bool = False
    walk_speed: str = "normal"
    route_sort: str = "fastest"


class RankCandidate(BaseModel):
    route_id: str
    mode: str
    duration_s: int
    distance_m: int
    cost: int = 0
    transfer_count: int = 0
    walk_distance_m: int = 0
    carbon_g: int = 0


class RankRequest(BaseModel):
    request_id: str
    user_context: RankUserContext
    candidates: list[RankCandidate]


class RankedRoute(BaseModel):
    route_id: str
    rank: int
    score: float
    reason: str


class RankResponse(BaseModel):
    ranked: list[RankedRoute]
    model_version: str = "heuristic-v1"
    fallback: bool = True


class PredictorPort:
    async def predict_eta(self, req: ETARequest) -> ETAResponse:
        raise NotImplementedError

    async def rank_routes(self, req: RankRequest) -> RankResponse:
        raise NotImplementedError


class HeuristicPredictor(PredictorPort):
    async def predict_eta(self, req: ETARequest) -> ETAResponse:
        total = 0
        for seg in req.segments:
            speed = 1.25 if req.mode in ("walk", "transit") else 8.0
            congestion = seg.congestion or 1
            total += int(seg.distance_m / max(speed, 0.5) * (1 + 0.15 * congestion))
        return ETAResponse(request_id=req.request_id, total_duration_s=max(total, 60))

    async def rank_routes(self, req: RankRequest) -> RankResponse:
        sort = req.user_context.route_sort

        def key(c: RankCandidate):
            if sort == "min_transfer":
                return (c.transfer_count, c.duration_s, c.walk_distance_m)
            if sort == "min_walk":
                return (c.walk_distance_m, c.duration_s, c.transfer_count)
            return (c.duration_s, c.transfer_count, c.walk_distance_m)

        ordered = sorted(req.candidates, key=key)
        ranked = [
            RankedRoute(
                route_id=c.route_id,
                rank=i,
                score=1.0 / i,
                reason="가장 빠른 경로" if i == 1 and sort == "fastest" else sort,
            )
            for i, c in enumerate(ordered, start=1)
        ]
        return RankResponse(ranked=ranked)
