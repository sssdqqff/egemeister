from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdate


def xp_for_level(level: int) -> int:
    return 100 * level * (level + 1) // 2


def calculate_level(xp: int) -> int:
    level = 1
    while xp >= xp_for_level(level):
        level += 1
    return level


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repository = ProfileRepository(db)

    async def get_profile(self, user_id: int) -> ProfileResponse:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return ProfileResponse.model_validate(profile)

    async def update_avatar(self, user_id: int, avatar_url: HttpUrl | None) -> ProfileResponse:
        profile = await self.profile_repository.update_profile(user_id, ProfileUpdate(avatar_url=avatar_url))
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        await self.db.commit()
        return ProfileResponse.model_validate(profile)

    async def admin_update_profile(self, user_id: int, profile_data: ProfileUpdate) -> ProfileResponse:
        profile = await self.profile_repository.update_profile(user_id, profile_data)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        await self.db.commit()
        return ProfileResponse.model_validate(profile)

    async def add_xp(self, user_id: int, amount: int, commit: bool = True) -> ProfileResponse:
        if amount < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="XP amount cannot be negative")
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        new_xp = profile.xp + amount
        new_level = calculate_level(new_xp)
        profile = await self.profile_repository.update_progress(profile, xp=new_xp, level=new_level, streak=profile.streak)
        if commit:
            await self.db.commit()
        return ProfileResponse.model_validate(profile)

    async def record_login(self, user_id: int, commit: bool = True) -> ProfileResponse:
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            profile = await self.profile_repository.create_profile(user_id)
        today = datetime.now(timezone.utc).date()
        streak = profile.streak
        if profile.last_login is None:
            streak = 1
        else:
            last_login_date = profile.last_login.astimezone(timezone.utc).date()
            days_passed = (today - last_login_date).days
            if days_passed == 1:
                streak += 1
            elif days_passed > 1:
                streak = 1
        profile = await self.profile_repository.update_progress(profile, xp=profile.xp, level=profile.level, streak=max(streak, 1))
        profile = await self.profile_repository.set_last_login(profile)
        if commit:
            await self.db.commit()
        return ProfileResponse.model_validate(profile)
