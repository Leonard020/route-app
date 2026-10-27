from fastapi import APIRouter, Depends, Query
from app.core.response import Envelope
from app.deps.auth import get_current_user, get_current_user_optional
from app.services.place_service import PlaceService

router = APIRouter()


@router.get("/recent")
async def recent_places(
    user=Depends(get_current_user_optional),
    svc: PlaceService = Depends(),
):
    data = await svc.recent(user=user)
    return Envelope(data=data)


@router.get("/search")
async def search_places(
    q: str = Query(..., min_length=1),
    lat: float | None = None,
    lng: float | None = None,
    radius_m: int = 3000,
    limit: int = 20,
    user=Depends(get_current_user_optional),
    svc: PlaceService = Depends(),
):
    data = await svc.search(q, lat=lat, lng=lng, radius_m=radius_m, limit=limit, user=user)
    return Envelope(data=data)


@router.get("/{place_id}")
async def place_detail(place_id: str, svc: PlaceService = Depends()):
    data = await svc.get_detail(place_id)
    return Envelope(data=data)


@router.delete("/recent/{recent_id}")
async def delete_recent(
    recent_id: str,
    user=Depends(get_current_user),
    svc: PlaceService = Depends(),
):
    data = await svc.delete_recent(recent_id, user)
    return Envelope(data=data)
