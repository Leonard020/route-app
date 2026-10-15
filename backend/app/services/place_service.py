from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.session import get_db
from app.repositories.place_repo import PlaceRepository
from app.repositories.recent_search_repo import RecentSearchRepository  # 신규


class PlaceService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.places = PlaceRepository(db)
        self.recent = RecentSearchRepository(db)

    async def search(
        self,
        q: str,
        *,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_m: int = 3000,
        limit: int = 20,
        user=None,
    ) -> dict:
        items = await self.places.search(q, lat=lat, lng=lng, radius_m=radius_m, limit=limit)
        if user:
            await self.recent.add(user_id=user.id, keyword=q, lat=lat, lng=lng)
            await self.db.commit()
        return {
            "items": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "address": p.address,
                    "category": p.category,
                    "lat": p.lat,
                    "lng": p.lng,
                }
                for p in items
            ]
        }

    async def get_detail(self, place_id) -> dict:
        p = await self.places.get(place_id)
        if not p:
            raise NotFoundError("place not found")
        return {
            "id": str(p.id),
            "name": p.name,
            "address": p.address,
            "road_address": p.road_address,
            "category": p.category,
            "lat": p.lat,
            "lng": p.lng,
            "phone": p.phone,
            "opening_hours": p.opening_hours,
            "rating": float(p.rating) if p.rating else None,
        }