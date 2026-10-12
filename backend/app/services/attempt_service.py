from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import SessionStatus
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.attempt import AttemptCreate, AttemptResponse


def normalize_answer(value: str) -> str:
    value = " ".join(value.strip().lower().split())
    return value.replace("ё", "е").replace(",", ".")


def is_answer_correct(correct: str, given: str) -> bool:
    correct_norm = normalize_answer(correct)
    given_norm = normalize_answer(given)
    if correct_norm == given_norm:
        return True
    try:
        return Decimal(correct_norm) == Decimal(given_norm)
    except InvalidOperation:
        return False


class AttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.attempt_repository = AttemptRepository(db)
        self.session_repository = SessionRepository(db)
        self.task_repository = TaskRepository(db)

    async def submit_attempt(self, user_id: int, attempt_data: AttemptCreate) -> AttemptResponse:
        task = await self.task_repository.get_by_id(attempt_data.task_id)
        if not task or not task.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        if attempt_data.session_id is not None:
            session = await self.session_repository.get_user_session(attempt_data.session_id, user_id)
            if not session:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
            if session.status != SessionStatus.IN_PROGRESS:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is already finished")
            if session.time_limit_seconds is not None:
                elapsed = (datetime.now(timezone.utc) - session.created_at).total_seconds()
                if elapsed > session.time_limit_seconds:
                    await self.session_repository.finish_session(session, SessionStatus.COMPLETED)
                    await self.db.commit()
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session time limit exceeded")
            if await self.attempt_repository.has_attempt(user_id, attempt_data.task_id, attempt_data.session_id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task already answered in this session")

        attempt = await self.attempt_repository.create_attempt(
            user_id=user_id,
            task_id=task.id,
            user_answer=attempt_data.user_answer,
            is_correct=is_answer_correct(task.answer, attempt_data.user_answer),
            session_id=attempt_data.session_id,
        )
        await self.db.commit()
        return AttemptResponse.model_validate(attempt)

    async def get_attempt_by_id(self, attempt_id: int, user_id: int) -> AttemptResponse:
        attempt = await self.attempt_repository.get_by_id(attempt_id)
        if not attempt or attempt.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
        return AttemptResponse.model_validate(attempt)

    async def get_user_attempts(
        self,
        user_id: int,
        task_id: Optional[int] = None,
        session_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AttemptResponse]:
        attempts = await self.attempt_repository.get_user_attempts(
            user_id=user_id,
            task_id=task_id,
            session_id=session_id,
            limit=limit,
            offset=offset,
        )
        return [AttemptResponse.model_validate(attempt) for attempt in attempts]

    async def get_session_attempts(self, session_id: int, user_id: int) -> List[AttemptResponse]:
        session = await self.session_repository.get_user_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        attempts = await self.attempt_repository.get_session_attempts(session_id)
        return [AttemptResponse.model_validate(attempt) for attempt in attempts]