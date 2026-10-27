from fastapi import APIRouter, Depends
from app.core.response import Envelope
from app.deps.auth import get_current_user
from app.schemas.settings import PreferenceOut, PreferenceUpdate
from app.services.preference_service import PreferenceService

router = APIRouter()


@router.get("", response_model=Envelope[PreferenceOut])
async def get_settings(
    user=Depends(get_current_user),
    svc: PreferenceService = Depends(),
):
    return Envelope(data=await svc.get(user))


@router.patch("", response_model=Envelope[PreferenceOut])
async def update_settings(
    payload: PreferenceUpdate,
    user=Depends(get_current_user),
    svc: PreferenceService = Depends(),
):
    return Envelope(data=await svc.update(user, payload))
