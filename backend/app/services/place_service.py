from typing import Optional
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.recent_search import RecentSearch
from app.repositories.place_repo import PlaceRepository
from app.repositories.recent_search_repo import RecentSearchRepository


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
        stations = await self.places.search_stations(q, limit=limit)
        if user:
            await self.recent.add(user_id=user.id, keyword=q, lat=lat, lng=lng)
            await self.db.commit()
        payload = [
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
        known = {(p.name, p.lat, p.lng) for p in items}
        for st in stations:
            if not st.lat or not st.lng:
                payload.append({
                    "id": st.station_id,
                    "name": st.station_name,
                    "address": st.line_name or "",
                    "category": "subway",
                    "lat": st.lat,
                    "lng": st.lng,
                    "station_id": st.station_id,
                    "subway_id": st.subway_id,
                })
                continue
            if (st.station_name, st.lat, st.lng) in known:
                continue
            payload.append({
                "id": st.station_id,
                "name": st.station_name,
                "address": st.line_name or "",
                "category": "subway",
                "lat": st.lat,
                "lng": st.lng,
                "station_id": st.station_id,
                "subway_id": st.subway_id,
            })
        return {
            "items": payload[:limit],
            "message": None if payload else "검색 결과가 없습니다. 다른 검색어로 입력해주세요.",
        }

    async def recent(self, user=None) -> dict:
        if not user:
            return {"items": [], "message": "최근 검색 내역이 없습니다."}
        rows = (
            await self.db.execute(
                select(RecentSearch)
                .where(RecentSearch.user_id == user.id)
                .order_by(RecentSearch.searched_at.desc())
                .limit(20)
            )
        ).scalars().all()
        if not rows:
            return {"items": [], "message": "최근 검색 내역이 없습니다."}
        return {
            "items": [
                {
                    "id": str(r.id),
                    "keyword": r.keyword,
                    "lat": r.lat,
                    "lng": r.lng,
                    "searched_at": r.searched_at,
                }
                for r in rows
            ]
        }

    async def delete_recent(self, recent_id, user) -> dict:
        from uuid import UUID
        row = await self.db.get(RecentSearch, UUID(str(recent_id)))
        if not row or (user and row.user_id != user.id):
            raise NotFoundError("검색 기록이 없습니다.")
        await self.db.delete(row)
        await self.db.commit()
        return {"deleted": True}

    async def get_detail(self, place_id) -> dict:
        from uuid import UUID
        try:
            p = await self.places.get(UUID(str(place_id)))
        except ValueError:
            p = None
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