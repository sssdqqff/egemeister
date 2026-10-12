from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    from .topic import Topic
    from .attempt import Attempt
    from .prototype import Prototype


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Task(Base):
    __tablename__ = "tasks"

    condition: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(SqlEnum(TaskDifficulty), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    topic: Mapped["Topic"] = relationship("Topic", back_populates="tasks", lazy="raise")

    prototype_id: Mapped[int] = mapped_column(ForeignKey("prototypes.id", ondelete="RESTRICT"), nullable=False, index=True)
    prototype: Mapped["Prototype"] = relationship("Prototype", back_populates="tasks", lazy="raise")

    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="task", lazy="raise")
