from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_current_admin, get_user_service
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PasswordChange


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user_data)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    return user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_user(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user.id, user_data)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(user.id, password_data)


@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    user: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.get_all_users()


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int,
    user: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def admin_update_user(
    user_id: int,
    user_data: UserUpdate,
    user: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user: User = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)
