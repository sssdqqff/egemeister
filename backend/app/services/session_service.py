from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, SessionStatus
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionResponse
from app.schemas.task import TaskResponse
from app.services.task_service import TaskService


class SessionSummary(BaseModel):
    session_id: int
    status: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    duration_seconds: int


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repository = SessionRepository(db)
        self.attempt_repository = AttemptRepository(db)
        self.task_service = TaskService(db)

    async def _get_owned_session(self, session_id: int, user_id: int) -> Session:
        session = await self.session_repository.get_user_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session

    async def _close_if_expired(self, session: Session) -> Session:
        if session.status != SessionStatus.IN_PROGRESS or session.time_limit_seconds is None:
            return session
        elapsed = (datetime.now(timezone.utc) - session.created_at).total_seconds()
        if elapsed > session.time_limit_seconds:
            await self.session_repository.finish_session(session, SessionStatus.COMPLETED)
            await self.db.commit()
        return session

    async def create_session(self, user_id: int, session_data: SessionCreate) -> SessionResponse:
        active = await self.session_repository.get_active_session(user_id, session_data.type)
        if active:
            active = await self._close_if_expired(active)
            if active.status == SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You already have an active session of this type",
                )
        kwargs = {}
        for field in ("title", "time_limit_seconds", "difficulty"):
            value = getattr(session_data, field, None)
            if value is not None:
                kwargs[field] = value
        session = await self.session_repository.create_session(
            user_id=user_id,
            session_type=session_data.type,
            **kwargs,
        )
        await self.db.commit()
        return SessionResponse.model_validate(session)

    async def get_session_by_id(self, session_id: int, user_id: int) -> SessionResponse:
        session = await self._get_owned_session(session_id, user_id)
        session = await self._close_if_expired(session)
        return SessionResponse.model_validate(session)

    async def get_user_sessions(
        self,
        user_id: int,
        session_type: Optional[str] = None,
        session_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SessionResponse]:
        sessions = await self.session_repository.get_user_sessions(
            user_id=user_id,
            session_type=session_type,
            status=session_status,
            limit=limit,
            offset=offset,
        )
        return [SessionResponse.model_validate(session) for session in sessions]

    async def get_session_tasks(
        self,
        session_id: int,
        user_id: int,
        topic_id: int,
        count: int = 10,
        prototype_id: Optional[int] = None,
        difficulty: Optional[str] = None,
    ) -> List[TaskResponse]:
        session = await self._get_owned_session(session_id, user_id)
        session = await self._close_if_expired(session)
        if session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is already finished")
        answered_ids = await self.attempt_repository.get_answered_task_ids(user_id, session_id)
        return await self.task_service.get_random_tasks(
            topic_id=topic_id,
            count=count,
            prototype_id=prototype_id,
            difficulty=difficulty,
            exclude_ids=answered_ids,
        )

    async def finish_session(self, session_id: int, user_id: int) -> SessionResponse:
        return await self._close_session(session_id, user_id, SessionStatus.COMPLETED)

    async def abandon_session(self, session_id: int, user_id: int) -> SessionResponse:
        return await self._close_session(session_id, user_id, SessionStatus.ABANDONED)

    async def _close_session(self, session_id: int, user_id: int, new_status: SessionStatus) -> SessionResponse:
        session = await self._get_owned_session(session_id, user_id)
        if session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is already finished")
        session = await self.session_repository.finish_session(session, new_status)
        await self.db.commit()
        return SessionResponse.model_validate(session)

    async def get_session_summary(self, session_id: int, user_id: int) -> SessionSummary:
        session = await self._get_owned_session(session_id, user_id)
        attempts = await self.attempt_repository.get_session_attempts(session_id)
        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt.is_correct)
        end = session.finished_at or datetime.now(timezone.utc)
        return SessionSummary(
            session_id=session.id,
            status=session.status.value,
            total_attempts=total,
            correct_attempts=correct,
            accuracy=round(correct / total * 100, 1) if total else 0.0,
            duration_seconds=int((end - session.created_at).total_seconds()),
        )