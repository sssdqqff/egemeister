from sqlalchemy import Integer, String, func, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.database import Base
from app.models.user import User

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .attempt import Attempt

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    session_type: Mapped[str] = mapped_column(String, nullable=False, default="practice")  #exam, challenge. practice
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    status: Mapped[str] = mapped_column(String, default="in_progress")  #completed, in_progress, abandoned
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    difficulty: Mapped[str] = mapped_column(String, default="medium", nullable=False)  # easy, medium, hard

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="session", cascade="all, delete-orphan")