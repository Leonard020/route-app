from fastapi import APIRouter
from app.api.v1 import auth, bus, places, routes, settings, subway

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(bus.router, prefix="/bus", tags=["bus"])
api_router.include_router(subway.router, prefix="/subway", tags=["subway"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
