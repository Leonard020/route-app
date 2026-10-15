from typing import Optional
from sqlalchemy import select
from app.models.user import User
from app.models.user_preference import UserPreference
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def find_by_email(self, email: str) -> Optional[User]:
        q = select(User).where(User.email == email, User.deleted_at.is_(None))
        return (await self.session.execute(q)).scalar_one_or_none()

    async def find_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        q = select(User).where(
            User.provider == provider, User.provider_id == provider_id
        )
        return (await self.session.execute(q)).scalar_one_or_none()

    async def get_preferences(self, user_id) -> Optional[UserPreference]:
        q = select(UserPreference).where(UserPreference.user_id == user_id)
        return (await self.session.execute(q)).scalar_one_or_none()