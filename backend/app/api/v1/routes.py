from fastapi import APIRouter, Depends, status
from app.core.response import Envelope
from app.deps.auth import get_current_user, get_current_user_optional
from app.schemas.route import (
    RouteRecommendRequest, RouteRecommendResponse,
    RerouteRequest, RerouteResponse, FeedbackCreate,
)
from app.services.route_service import RouteService

router = APIRouter()


@router.post("/recommend", response_model=Envelope[RouteRecommendResponse])
async def recommend(
    payload: RouteRecommendRequest,
    user=Depends(get_current_user_optional),
    svc: RouteService = Depends(),
):
    result = await svc.recommend(payload, user)
    return Envelope(data=result["data"], meta=result["meta"])


@router.get("/{route_id}", response_model=Envelope[dict])
async def detail(route_id: str, svc: RouteService = Depends()):
    data = await svc.get_detail(route_id)
    return Envelope(data=data)


@router.post("/{route_id}/reroute", response_model=Envelope[RerouteResponse])
async def reroute(
    route_id: str,
    payload: RerouteRequest,
    svc: RouteService = Depends(),
):
    data = await svc.reroute(route_id, payload)
    return Envelope(data=data)


@router.post(
    "/{route_id}/feedback",
    status_code=status.HTTP_201_CREATED,
    response_model=Envelope[dict],
)
async def feedback(
    route_id: str,
    payload: FeedbackCreate,
    user=Depends(get_current_user_optional),
    svc: RouteService = Depends(),
):
    data = await svc.feedback(route_id, payload, user)
    return Envelope(data=data)