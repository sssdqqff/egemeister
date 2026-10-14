from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SessionType = Literal["practice", "exam", "challenge"]
SessionStatus = Literal["in_progress", "completed", "abandoned"]
SessionDifficulty = Literal["easy", "medium", "hard"]


class SessionCreate(BaseModel):
    type: SessionType = Field(default="practice")
    title: str | None = Field(default=None, max_length=200)
    time_limit_seconds: int | None = Field(default=None, gt=0)
    difficulty: SessionDifficulty = Field(default="easy")

    model_config = ConfigDict(extra="forbid")


class SessionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)

    model_config = ConfigDict(extra="forbid")


class SessionResponse(BaseModel):
    id: int
    user_id: int
    type: SessionType = Field(validation_alias="session_type")
    status: SessionStatus
    created_at: datetime
    finished_at: datetime | None
    title: str | None
    time_limit_seconds: int | None
    difficulty: SessionDifficulty

    model_config = ConfigDict(from_attributes=True)