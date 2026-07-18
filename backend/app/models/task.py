from sqlalchemy import DateTime, Integer, String, Text, func, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from enum import Enum

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .topic import Topic
    from .attempt import Attempt
    from .subject import Subject

class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Task(Base):
    __tablename__ = "tasks"

    condition: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(SqlEnum(TaskDifficulty), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    topic: Mapped["Topic"] = relationship("Topic", back_populates="tasks")
    
    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="task", cascade="all, delete-orphan")