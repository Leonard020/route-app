from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.db.session import get_db
from app.domain import messages
from app.domain.geo import haversine_m
from app.engines.graph import GraphProvider


class LocationService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        graph: GraphProvider = Depends(),
    ):
        self.db = db
        self.graph = graph

    async def resolve(
        self,
        *,
        lat: float | None,
        lng: float | None,
        accuracy_m: float | None = None,
        permission: bool = True,
    ) -> dict:
        if not permission:
            raise ValidationError(messages.LOCATION_DENIED)
        if lat is None or lng is None:
            raise ValidationError(messages.LOCATION_FAILED)
        place = await self.graph.nearest_place(lat, lng, max_m=800)
        if not place:
            raise ValidationError(messages.LOCATION_FAILED)
        warning = None
        if accuracy_m is not None and accuracy_m > 80:
            warning = messages.LOCATION_LOW_ACCURACY
        return {
            "lat": lat,
            "lng": lng,
            "name": place.name,
            "address": place.address,
            "place_id": str(place.id),
            "category": place.category,
            "distance_m": int(haversine_m(lat, lng, place.lat, place.lng)),
            "warning": warning,
        }
