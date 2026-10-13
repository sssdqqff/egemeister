from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.rate_limit import login_limiter
from app.repositories.auth_repository import AuthRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import BotLoginCodeResponse
from app.security import (
    generate_login_code,
    generate_session_token,
    hash_login_code,
    hash_session_token,
)
from app.services.profile_service import ProfileService

MAX_CODE_GENERATION_TRIES = 5


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repository = AuthRepository(db)
        self.user_repository = UserRepository(db)
        self.profile_repository = ProfileRepository(db)
        self.profile_service = ProfileService(db)

    async def _get_or_create_user(self, telegram_id: int, first_name: str | None) -> User:
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if user:
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            return user
        try:
            user = await self.user_repository.create_telegram_user(telegram_id, first_name)
            await self.profile_repository.create_profile(user.id)
        except IntegrityError:
            await self.db.rollback()
            user = await self.user_repository.get_by_telegram_id(telegram_id)
            if user is None:
                raise
        return user

    async def issue_login_code(self, telegram_id: int, first_name: str | None) -> BotLoginCodeResponse:
        now = utcnow()
        user = await self._get_or_create_user(telegram_id, first_name)
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated")
        await self.auth_repository.invalidate_user_codes(user.id, now)
        for _ in range(MAX_CODE_GENERATION_TRIES):
            code = generate_login_code()
            code_hash = hash_login_code(code)
            if not await self.auth_repository.has_active_code(code_hash, now):
                break
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Try again in a moment")
        expires_at = now + timedelta(seconds=settings.login_code_ttl_seconds)
        await self.auth_repository.create_login_code(user.id, code_hash, expires_at)
        await self.db.commit()
        return BotLoginCodeResponse(code=code, expires_in=settings.login_code_ttl_seconds)

    async def exchange_code(self, code: str, client_key: str) -> tuple[User, str]:
        if login_limiter.is_blocked(client_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts, try again later",
            )
        now = utcnow()
        user_id = await self.auth_repository.consume_login_code(hash_login_code(code), now)
        user = await self.user_repository.get_by_id(user_id) if user_id else None
        if user is None or not user.is_active:
            login_limiter.register_failure(client_key)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")
        token = generate_session_token()
        expires_at = now + timedelta(days=settings.session_ttl_days)
        await self.auth_repository.create_auth_session(user.id, hash_session_token(token), expires_at)
        await self.profile_service.record_login(user.id, commit=False)
        await self.db.commit()
        return user, token

    async def get_user_by_session_token(self, token: str) -> User:
        auth_session = await self.auth_repository.get_active_session(hash_session_token(token), utcnow())
        user = await self.user_repository.get_by_id(auth_session.user_id) if auth_session else None
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return user

    async def logout(self, token: str) -> None:
        await self.auth_repository.revoke_session(hash_session_token(token), utcnow())
        await self.db.commit()

    async def logout_everywhere(self, user_id: int) -> None:
        await self.auth_repository.revoke_all_user_sessions(user_id, utcnow())
        await self.db.commit()