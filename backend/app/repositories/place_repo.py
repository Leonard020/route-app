from typing import Optional, Sequence
from sqlalchemy import select
from app.domain.geo import haversine_m
from app.models.place import Place
from app.models.subway_station import SubwayStation
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
        if q:
            stmt = stmt.where(Place.name.ilike(f"%{q}%"))
        rows = list((await self.session.execute(stmt.limit(100))).scalars().all())
        if lat is not None and lng is not None:
            rows = [
                p for p in rows
                if haversine_m(lat, lng, p.lat, p.lng) <= radius_m
            ]
            rows.sort(key=lambda p: haversine_m(lat, lng, p.lat, p.lng))
        return rows[:limit]

    async def search_stations(self, q: str, limit: int = 20) -> Sequence[SubwayStation]:
        stmt = select(SubwayStation).where(
            SubwayStation.station_name.ilike(f"%{q}%")
        ).limit(limit)
        return (await self.session.execute(stmt)).scalars().all()

    async def get_or_create_from_external(self, data: dict) -> Place:
        if data.get("external_id"):
            existing = (
                await self.session.execute(
                    select(Place).where(Place.external_id == data["external_id"])
                )
            ).scalar_one_or_none()
            if existing:
                return existing
        place = Place(**data)
        self.session.add(place)
        await self.session.flush()
        return place
