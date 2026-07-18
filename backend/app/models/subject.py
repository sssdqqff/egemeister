from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .topic import Topic


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topics: Mapped[list["Topic"]] = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")