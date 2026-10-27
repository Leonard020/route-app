from typing import Optional, List, Tuple, Any
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.catalog.places import nearest_catalog
from app.db.session import get_db
from app.domain.geo import haversine_m
from app.models.place import Place


class GraphProvider:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def neighbors(self, node_id: str, mode: str) -> List[Tuple[str, float, dict]]:
        return []

    async def nearest_node(self, lat: float, lng: float) -> Optional[str]:
        place = await self.nearest_place(lat, lng)
        return str(place.id) if place else None

    async def nearest_place(
        self,
        lat: float,
        lng: float,
        category: str | None = None,
        max_m: float = 2000,
    ) -> Any:
        try:
            stmt = select(Place)
            if category:
                stmt = stmt.where(Place.category == category)
            rows = (await self.db.execute(stmt)).scalars().all()
            if rows:
                ranked = sorted(rows, key=lambda p: haversine_m(lat, lng, p.lat, p.lng))
                best = ranked[0]
                if haversine_m(lat, lng, best.lat, best.lng) <= max_m:
                    return best
        except Exception:
            pass
        return nearest_catalog(lat, lng, category=category, max_m=max_m)
