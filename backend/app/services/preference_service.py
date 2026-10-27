from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user_preference import UserPreference
from app.schemas.settings import PreferenceOut, PreferenceUpdate


class PreferenceService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_or_create(self, user) -> UserPreference:
        pref = await self.db.scalar(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
        if pref:
            return pref
        pref = UserPreference(user_id=user.id)
        self.db.add(pref)
        await self.db.commit()
        await self.db.refresh(pref)
        return pref

    async def get(self, user) -> PreferenceOut:
        pref = await self.get_or_create(user)
        return PreferenceOut(
            walk_speed=pref.walk_speed,
            route_sort=pref.route_sort,
            alert_alight=pref.alert_alight,
            alert_transfer=pref.alert_transfer,
            alert_minutes_before=pref.alert_minutes_before,
            notify_enabled=pref.notify_enabled,
            max_walk_min=pref.max_walk_min,
            accessibility=pref.accessibility,
        )

    async def update(self, user, payload: PreferenceUpdate) -> PreferenceOut:
        pref = await self.get_or_create(user)
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(pref, key, value)
        await self.db.commit()
        return await self.get(user)
