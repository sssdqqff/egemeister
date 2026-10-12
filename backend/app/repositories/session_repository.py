from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import Session, SessionDifficulty, SessionStatus, SessionType


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: int,
        session_type: SessionType = SessionType.PRACTICE,
        title: Optional[str] = None,
        time_limit_seconds: Optional[int] = None,
        difficulty: SessionDifficulty = SessionDifficulty.EASY,
    ) -> Session:
        session = Session(
            user_id=user_id,
            session_type=SessionType(session_type),
            title=title,
            time_limit_seconds=time_limit_seconds,
            difficulty=SessionDifficulty(difficulty),
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: int) -> Optional[Session]:
        return await self.db.get(Session, session_id)

    async def get_user_session(self, session_id: int, user_id: int) -> Optional[Session]:
        stmt = select(Session).where(Session.id == session_id, Session.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_with_attempts(self, session_id: int) -> Optional[Session]:
        stmt = select(Session).options(selectinload(Session.attempts)).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        user_id: int,
        session_type: Optional[SessionType] = None,
        status: Optional[SessionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Session]:
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if session_type is not None:
            stmt = stmt.where(Session.session_type == SessionType(session_type))
        if status is not None:
            stmt = stmt.where(Session.status == SessionStatus(status))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_active_session(self, user_id: int, session_type: Optional[SessionType] = None) -> Optional[Session]:
        stmt = (
            select(Session)
            .where(Session.user_id == user_id, Session.status == SessionStatus.IN_PROGRESS)
            .order_by(Session.created_at.desc())
            .limit(1)
        )
        if session_type is not None:
            stmt = stmt.where(Session.session_type == SessionType(session_type))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def finish_session(self, session: Session, status: SessionStatus = SessionStatus.COMPLETED) -> Session:
        session.status = SessionStatus(status)
        session.finished_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(session)
        return session