from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, profile_id: int) -> Optional[Profile]:
        return await self.db.get(Profile, profile_id)

    async def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        result = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_profile(self, user_id: int, profile_data: Optional[ProfileCreate] = None) -> Profile:
        values = profile_data.model_dump(mode="json") if profile_data else {}
        new_profile = Profile(user_id=user_id, **values)
        self.db.add(new_profile)
        await self.db.flush()
        await self.db.refresh(new_profile)
        return new_profile

    async def update_profile(self, user_id: int, profile_data: ProfileUpdate) -> Optional[Profile]:
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        for key, value in profile_data.model_dump(exclude_unset=True, mode="json").items():
            setattr(profile, key, value)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_progress(self, profile: Profile, xp: int, level: int, streak: int) -> Profile:
        profile.xp = xp
        profile.level = level
        profile.streak = streak
        await self.db.flush()
        return profile

    async def set_last_login(self, profile: Profile) -> Profile:
        profile.last_login = datetime.now(timezone.utc)
        await self.db.flush()
        return profile