from typing import Sequence
from sqlalchemy import select, func
from app.models.feedback import Feedback
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    model = Feedback

    async def avg_rating_by_route(self, route_id) -> float | None:
        q = select(func.avg(Feedback.rating)).where(Feedback.route_id == route_id)
        return (await self.session.execute(q)).scalar()

    async def list_by_route(self, route_id) -> Sequence[Feedback]:
        q = select(Feedback).where(Feedback.route_id == route_id).order_by(
            Feedback.created_at.desc()
        )
        return (await self.session.execute(q)).scalars().all()