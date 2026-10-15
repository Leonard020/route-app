from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.route import Route
from app.models.route_step import RouteStep
from app.models.step_segment import StepSegment
from app.repositories.base import BaseRepository


class RouteRepository(BaseRepository[Route]):
    model = Route

    async def get_with_steps(self, route_id) -> Optional[Route]:
        q = (
            select(Route)
            .where(Route.id == route_id)
            .options(selectinload(Route.steps).selectinload(RouteStep.segments))
        )
        return (await self.session.execute(q)).scalar_one_or_none()

    async def add_with_steps(self, route: Route, steps: list[dict]) -> Route:
        self.session.add(route)
        await self.session.flush()
        for s in steps:
            segments = s.pop("segments", [])
            step = RouteStep(route_id=route.id, **s)
            self.session.add(step)
            await self.session.flush()
            for seg in segments:
                self.session.add(StepSegment(step_id=step.id, **seg))
        await self.session.flush()
        return route

    async def recent_by_user(self, user_id, limit: int = 20) -> Sequence[Route]:
        q = (
            select(Route)
            .where(Route.user_id == user_id)
            .order_by(Route.created_at.desc())
            .limit(limit)
        )
        return (await self.session.execute(q)).scalars().all()