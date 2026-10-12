from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .subject import Subject
    from .task import Task


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
    UniqueConstraint("subject_id", "number", name="uq_topics_subject_number"),
    UniqueConstraint("subject_id", "slug", name="uq_topics_subject_slug"),
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False)  # номер задания КИМ
    name: Mapped[str] = mapped_column(String, nullable=False)     # например "Логические выражения"
    slug: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False,)
    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics", lazy="raise")

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="topic", lazy="raise")