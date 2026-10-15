from datetime import datetime
from typing import List
from app.ports.predictor import (
    PredictorPort, ETARequest, ETASegmentIn, ETAResponse,
)


class ETAService:
    def __init__(self, predictor: PredictorPort):
        self.predictor = predictor

    async def predict(
        self,
        request_id: str,
        route_id: str,
        segments: List[ETASegmentIn],
        depart_at: datetime,
        mode: str,
    ) -> ETAResponse:
        req = ETARequest(
            request_id=route_id,  # 매핑 위해 route_id를 request_id로
            route_id=route_id,
            segments=segments,
            depart_at=depart_at,
            mode=mode,
        )
        return await self.predictor.predict_eta(req)