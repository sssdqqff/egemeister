from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime


class ProfileCreate(BaseModel):
    avatar_url: HttpUrl | None = Field(None, description="User avatar URL")


class ProfileUpdate(BaseModel):
    avatar_url: HttpUrl | None = Field(None)
    xp: int | None = Field(None, ge=0)
    level: int | None = Field(None, ge=1)
    streak: int | None = Field(None, ge=0)


class ProfileResponse(BaseModel):
    id: int
    avatar_url: HttpUrl | None
    xp: int = Field(..., ge=0, description="Experience points")
    level: int = Field(..., ge=1, description="User level")
    streak: int = Field(..., ge=0, description="Login streak")
    last_login: datetime | None = Field(None)

    model_config = ConfigDict(from_attributes=True)