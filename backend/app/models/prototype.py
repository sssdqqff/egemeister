from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .task import Task


class Prototype(Base):
    __tablename__ = "prototypes"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exam_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true(), nullable=False)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="prototype", lazy="raise")
