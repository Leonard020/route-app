from datetime import datetime
from app.models.prediction import Prediction
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    model = Prediction

    async def log(
        self,
        *,
        route_id,
        predictor_version: str,
        kind: str,
        request: dict,
        response: dict,
        latency_ms: int,
        fallback_used: bool,
    ) -> Prediction:
        pred = Prediction(
            route_id=route_id,
            predictor_version=predictor_version,
            kind=kind,
            request=request,
            response=response,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
        )
        return await self.add(pred)

    async def attach_actual(self, prediction_id, actual: dict) -> None:
        pred = await self.get(prediction_id)
        if pred:
            pred.actual = actual
            await self.session.flush()