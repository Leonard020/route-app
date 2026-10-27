from fastapi import APIRouter, Depends
from app.core.response import Envelope
from app.deps.auth import get_current_user_optional
from app.schemas.guidance import GuidanceOut, GuidanceStartRequest, GuidanceTickRequest
from app.services.guidance_service import GuidanceService

router = APIRouter()


@router.post("/start", response_model=Envelope[GuidanceOut])
async def start(
    payload: GuidanceStartRequest,
    user=Depends(get_current_user_optional),
    svc: GuidanceService = Depends(),
):
    return Envelope(data=await svc.start(payload, user))


@router.post("/{session_id}/tick", response_model=Envelope[GuidanceOut])
async def tick(
    session_id: str,
    payload: GuidanceTickRequest,
    user=Depends(get_current_user_optional),
    svc: GuidanceService = Depends(),
):
    return Envelope(data=await svc.tick(session_id, payload, user))


@router.post("/{session_id}/end", response_model=Envelope[GuidanceOut])
async def end(session_id: str, svc: GuidanceService = Depends()):
    return Envelope(data=await svc.end(session_id))


@router.get("/{session_id}", response_model=Envelope[GuidanceOut])
async def detail(session_id: str, svc: GuidanceService = Depends()):
    return Envelope(data=await svc.get(session_id))
