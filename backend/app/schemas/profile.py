from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class ProfileCreate(BaseModel):
    avatar_url: str | None = Field(None, description="User avatar URL")


class ProfileUpdate(BaseModel):
    avatar_url: str | None = Field(None)
    xp: int | None = Field(None)
    level: int | None = Field(None)
    streak: int | None = Field(None)


class ProfileResponse(BaseModel):
    id: int = Field(..., description="Profile unique identifier")
    avatar_url: str | None = Field(None)
    xp: int = Field(..., description="Experience points")
    level: int = Field(..., description="User level")
    streak: int = Field(..., description="Login streak")
    last_login: datetime | None = Field(None)

    model_config = ConfigDict(from_attributes=True)