from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=20)
    email: EmailStr | None = Field(None)


class UserResponse(BaseModel):
    id: int = Field(..., description="User unique identifier")
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., description="User email")
    is_active: bool = Field(..., description="Is user active")
    role: str = Field(..., description="User role (e.g., 'user', 'admin')")
    created_at: datetime = Field(..., description="Account creation time")
    last_login: datetime | None = Field(None, description="Last login time")

    model_config = ConfigDict(from_attributes=True)