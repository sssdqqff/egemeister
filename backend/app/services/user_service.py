from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.services.profile_service import ProfileService


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.profile_repository = ProfileRepository(db)
        self.profile_service = ProfileService(db)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)

    async def get_all_users(
        self,
        role: Optional[UserRole] = None,
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UserResponse]:
        users = await self.user_repository.get_all_users(
            role=role,
            only_active=only_active,
            limit=limit,
            offset=offset,
        )
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        changes = user_data.model_dump(exclude_unset=True)
        if any(value is None for value in changes.values()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be null")
        if "email" in changes:
            user_data.email = changes["email"].lower()
            existing = await self.user_repository.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if "username" in changes:
            existing = await self.user_repository.get_by_username(changes["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        try:
            user = await self.user_repository.update_user(user_id, user_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)

    async def deactivate_user(self, user_id: int) -> None:
        deactivated = await self.user_repository.deactivate_user(user_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.db.commit()