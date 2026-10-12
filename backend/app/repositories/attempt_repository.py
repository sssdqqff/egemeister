from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt


class AttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_attempt(
        self,
        user_id: int,
        task_id: int,
        user_answer: str,
        is_correct: bool,
        session_id: Optional[int] = None,
    ) -> Attempt:
        attempt = Attempt(
            user_id=user_id,
            task_id=task_id,
            user_answer=user_answer,
            is_correct=is_correct,
            session_id=session_id,
        )
        self.db.add(attempt)
        await self.db.flush()
        await self.db.refresh(attempt)
        return attempt

    async def get_by_id(self, attempt_id: int) -> Optional[Attempt]:
        return await self.db.get(Attempt, attempt_id)

    async def get_user_attempts(
        self,
        user_id: int,
        task_id: Optional[int] = None,
        session_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Attempt]:
        stmt = (
            select(Attempt)
            .where(Attempt.user_id == user_id)
            .order_by(Attempt.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if task_id is not None:
            stmt = stmt.where(Attempt.task_id == task_id)
        if session_id is not None:
            stmt = stmt.where(Attempt.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_session_attempts(self, session_id: int) -> List[Attempt]:
        stmt = select(Attempt).where(Attempt.session_id == session_id).order_by(Attempt.created_at)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_answered_task_ids(self, user_id: int, session_id: int) -> List[int]:
        stmt = select(Attempt.task_id).where(Attempt.user_id == user_id, Attempt.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def has_attempt(self, user_id: int, task_id: int, session_id: int) -> bool:
        stmt = (
            select(Attempt.id)
            .where(Attempt.user_id == user_id, Attempt.task_id == task_id, Attempt.session_id == session_id)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None