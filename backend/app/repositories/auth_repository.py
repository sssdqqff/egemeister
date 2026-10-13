from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.models.login_code import LoginCode


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_login_code(self, user_id: int, code_hash: str, expires_at: datetime) -> LoginCode:
        login_code = LoginCode(user_id=user_id, code_hash=code_hash, expires_at=expires_at)
        self.db.add(login_code)
        await self.db.flush()
        await self.db.refresh(login_code)
        return login_code

    async def has_active_code(self, code_hash: str, now: datetime) -> bool:
        stmt = (
            select(LoginCode.id)
            .where(LoginCode.code_hash == code_hash, LoginCode.used_at.is_(None), LoginCode.expires_at > now)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def invalidate_user_codes(self, user_id: int, now: datetime) -> int:
        stmt = (
            update(LoginCode)
            .where(LoginCode.user_id == user_id, LoginCode.used_at.is_(None))
            .values(used_at=now)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        return result.rowcount

    async def consume_login_code(self, code_hash: str, now: datetime) -> Optional[int]:
        stmt = (
            update(LoginCode)
            .where(LoginCode.code_hash == code_hash, LoginCode.used_at.is_(None), LoginCode.expires_at > now)
            .values(used_at=now)
            .returning(LoginCode.user_id)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_auth_session(self, user_id: int, token_hash: str, expires_at: datetime) -> AuthSession:
        auth_session = AuthSession(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(auth_session)
        await self.db.flush()
        await self.db.refresh(auth_session)
        return auth_session

    async def get_active_session(self, token_hash: str, now: datetime) -> Optional[AuthSession]:
        stmt = select(AuthSession).where(
            AuthSession.token_hash == token_hash,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_session(self, token_hash: str, now: datetime) -> bool:
        stmt = (
            update(AuthSession)
            .where(AuthSession.token_hash == token_hash, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def revoke_all_user_sessions(self, user_id: int, now: datetime) -> int:
        stmt = (
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        return result.rowcount