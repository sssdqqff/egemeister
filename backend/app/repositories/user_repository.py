from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.schemas.user import UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(
        self,
        role: Optional[UserRole] = None,
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        stmt = select(User).order_by(User.id).limit(limit).offset(offset)
        if role is not None:
            stmt = stmt.where(User.role == UserRole(role))
        if only_active:
            stmt = stmt.where(User.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> Optional[User]:
        stmt = select(User).where(or_(User.username == login, User.email == login))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_profile(self, user_id: int) -> Optional[User]:
        stmt = select(User).options(selectinload(User.profile)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole(role),
        )
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        await self.db.flush()
        return user

    async def deactivate_user(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.is_active = False
        await self.db.flush()
        return True

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create_telegram_user(self, telegram_id: int, first_name: Optional[str] = None) -> User:
        new_user = User(telegram_id=telegram_id, first_name=first_name)
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user