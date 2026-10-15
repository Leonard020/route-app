from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import AuthError
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.user_repo import UserRepository


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise AuthError("invalid authorization header")
    token = authorization[7:]
    claims = decode_token(token)
    if not claims or claims.get("typ") != "access":
        raise AuthError("invalid token")

    user = await UserRepository(db).get(claims["sub"])
    if not user or user.status != "active":
        raise AuthError("invalid user")
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    claims = decode_token(authorization[7:])
    if not claims:
        return None
    return await UserRepository(db).get(claims["sub"])