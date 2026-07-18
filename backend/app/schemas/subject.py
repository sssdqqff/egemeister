from pydantic import BaseModel, ConfigDict, Field

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Subject name")
    description: str = Field(..., min_length=10, max_length=500, description="Subject description")
    is_active: bool = Field(default=True, description="Indicates if the subject is active")


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, min_length=10, max_length=500)
    is_active: bool | None = Field(None, description="Indicates if the subject is active")


class SubjectResponse(BaseModel):
    id: int = Field(..., description="Subject unique identifier")
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    is_active: bool

    model_config = ConfigDict(from_attributes=True)