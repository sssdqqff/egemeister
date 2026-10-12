from fastapi import APIRouter, Depends, status
from pydantic import HttpUrl

from app.dependencies import get_current_user, get_profile_service
from app.models.user import User
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileResponse, ProfileAvatarUpdate


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(
    user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.get_profile(user.id)


@router.patch("/avatar", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_avatar(
    avatar_data: ProfileAvatarUpdate,
    user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.update_avatar(user.id, avatar_data.avatar_url)
