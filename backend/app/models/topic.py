from sqlalchemy import Integer, String, func, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .subject import Subject
    from .task import Task


class Topic(Base):
    __tablename__ = "topics"

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="topic", cascade="all, delete-orphan")