from sqlalchemy import Integer, String, func, ForeignKey, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from enum import Enum

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .attempt import Attempt
    from .user import User

class SessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class SessionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SessionType(str, Enum):
    PRACTICE = "practice"
    EXAM = "exam"
    CHALLENGE = "challenge"

class Session(Base):
    __tablename__ = "sessions"

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    session_type: Mapped[SessionType] = mapped_column(SqlEnum(SessionType), nullable=False, default=SessionType.PRACTICE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    status: Mapped[SessionStatus] = mapped_column(SqlEnum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    difficulty: Mapped[SessionDifficulty] = mapped_column(SqlEnum(SessionDifficulty), default=SessionDifficulty.EASY)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="session", cascade="all, delete-orphan")