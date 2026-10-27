from fastapi import APIRouter, Depends
from app.core.response import Envelope
from app.schemas.auth import SignupRequest, LoginRequest, RefreshRequest, TokenPair
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup")
async def signup(payload: SignupRequest, svc: AuthService = Depends()):
    return Envelope(data=await svc.signup(payload))


@router.post("/login", response_model=Envelope[TokenPair])
async def login(payload: LoginRequest, svc: AuthService = Depends()):
    return Envelope(data=await svc.login(payload))


@router.post("/refresh", response_model=Envelope[TokenPair])
async def refresh(payload: RefreshRequest, svc: AuthService = Depends()):
    return Envelope(data=await svc.refresh(payload))
