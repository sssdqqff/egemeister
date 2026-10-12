from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security import create_access_token, decode_access_token, hash_password, verify_password
from app.services.profile_service import ProfileService

MIN_PASSWORD_LENGTH = 6


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.profile_repository = ProfileRepository(db)
        self.profile_service = ProfileService(db)

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        email = user_data.email.lower()
        if await self.user_repository.get_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        if await self.user_repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        try:
            user = await self.user_repository.create_user(
                username=user_data.username,
                email=email,
                hashed_password=hash_password(user_data.password),
            )
            await self.profile_repository.create_profile(user.id)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        return UserResponse.model_validate(user)

    async def login(self, login: str, password: str) -> TokenResponse:
        login = login.strip()
        if "@" in login:
            login = login.lower()
        user = await self.user_repository.get_by_login(login)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated")
        await self.profile_service.record_login(user.id, commit=False)
        await self.db.commit()
        return TokenResponse(access_token=create_access_token(user.id))

    async def get_user_from_token(self, token: str) -> User:
        user_id = decode_access_token(token)
        user = await self.user_repository.get_by_id(user_id) if user_id else None
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

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

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        if len(new_password) < MIN_PASSWORD_LENGTH:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password is too short")
        await self.user_repository.update_password(user, hash_password(new_password))
        await self.db.commit()

    async def deactivate_user(self, user_id: int) -> None:
        deactivated = await self.user_repository.deactivate_user(user_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.db.commit()