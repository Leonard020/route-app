from typing import Optional, Sequence
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import UUID
from app.models.place import Place
from app.repositories.base import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    model = Place

    async def search(
        self,
        q: str,
        *,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_m: int = 3000,
        limit: int = 20,
    ) -> Sequence[Place]:
        stmt = select(Place)
        # 이름 유사도
        if q:
            stmt = stmt.where(Place.name.ilike(f"%{q}%"))
        # 반경 필터 (PostGIS)
        if lat is not None and lng is not None and Place.location.isnot(None):
            point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(
                Place.location.type
            )
            stmt = stmt.where(func.ST_DWithin(Place.location, point, radius_m))
            stmt = stmt.order_by(func.ST_Distance(Place.location, point))
        return (await self.session.execute(stmt.limit(limit))).scalars().all()

    async def get_or_create_from_external(self, data: dict) -> Place:
        if data.get("external_id"):
            q = select(Place).where(Place.external_id == data["external_id"])
            existing = (await self.session.execute(q)).scalar_one_or_none()
            if existing:
                return existing
        place = Place(**data)
        self.session.add(place)
        await self.session.flush()
        return place