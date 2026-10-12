from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

SessionType = Literal["practice", "exam", "challenge"]
SessionStatus = Literal["in_progress", "completed", "abandoned"]


class SessionCreate(BaseModel):
    type: SessionType = Field(default="practice", description="Session type")


class SessionUpdate(BaseModel):
    status: SessionStatus | None = Field(None, description="Session status")
    finished_at: datetime | None = Field(None, description="Finish time")


class SessionResponse(BaseModel):
    id: int = Field(..., description="Session ID")
    user_id: int = Field(..., description="User ID")
    type: SessionType = Field(..., description="Session type")
    status: SessionStatus = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Creation time")
    finished_at: datetime | None = Field(None, description="Finish time")

    model_config = ConfigDict(from_attributes=True)