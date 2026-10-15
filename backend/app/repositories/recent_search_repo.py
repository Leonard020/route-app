from typing import Optional
from app.models.recent_search import RecentSearch
from app.repositories.base import BaseRepository


class RecentSearchRepository(BaseRepository[RecentSearch]):
    model = RecentSearch

    async def add(
        self,
        *,
        user_id=None,
        place_id=None,
        keyword: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
    ) -> RecentSearch:
        obj = RecentSearch(
            user_id=user_id, place_id=place_id,
            keyword=keyword, lat=lat, lng=lng,
        )
        return await super().add(obj)