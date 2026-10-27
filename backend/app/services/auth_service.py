from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AuthError, ValidationError
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import SignupRequest, LoginRequest, RefreshRequest, TokenPair


class AuthService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.users = UserRepository(db)

    async def signup(self, payload: SignupRequest) -> dict:
        if await self.users.find_by_email(payload.email):
            raise ValidationError("email already exists", {"field": "email"})

        from app.models.user import User
        from app.models.user_preference import UserPreference
        user = User(
            email=payload.email,
            nickname=payload.nickname,
            password_hash=hash_password(payload.password),
            provider=payload.provider,
        )
        await self.users.add(user)
        await self.db.flush()
        self.db.add(UserPreference(user_id=user.id))
        await self.db.commit()

        return {
            "user_id": str(user.id),
            "access_token": create_access_token(str(user.id), {"role": user.role}),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    async def login(self, payload: LoginRequest) -> TokenPair:
        user = await self.users.find_by_email(payload.email)
        if not user or not user.password_hash:
            raise AuthError("invalid credentials")
        if not verify_password(payload.password, user.password_hash):
            raise AuthError("invalid credentials")
        if user.status != "active":
            raise AuthError("account disabled")

        return TokenPair(
            access_token=create_access_token(str(user.id), {"role": user.role}),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, payload: RefreshRequest) -> TokenPair:
        claims = decode_token(payload.refresh_token)
        if not claims or claims.get("typ") != "refresh":
            raise AuthError("invalid refresh token")
        user = await self.users.get(claims["sub"])
        if not user or user.status != "active":
            raise AuthError("invalid user")

        return TokenPair(
            access_token=create_access_token(str(user.id), {"role": user.role}),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def logout(self, user_id) -> None:
        # 토큰 블랙리스트는 Redis 도입 시 구현
        return None