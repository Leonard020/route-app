from fastapi import APIRouter, Depends, Query
from app.core.response import Envelope
from app.services.location_service import LocationService

router = APIRouter()


@router.get("/current")
async def current_location(
    lat: float | None = Query(None),
    lng: float | None = Query(None),
    accuracy_m: float | None = Query(None),
    permission: bool = Query(True),
    svc: LocationService = Depends(),
):
    data = await svc.resolve(lat=lat, lng=lng, accuracy_m=accuracy_m, permission=permission)
    return Envelope(data=data)
