from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=20)
    email: EmailStr | None = Field(None)

    model_config = ConfigDict(str_strip_whitespace=True)


class UserResponse(BaseModel):
    id: int
    telegram_id: int | None = None
    first_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)