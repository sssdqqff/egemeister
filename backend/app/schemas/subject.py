from pydantic import BaseModel, Field, ConfigDict


class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    slug: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    is_active: bool = True


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    slug: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, min_length=10, max_length=500)
    is_active: bool | None = None


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str
    is_active: bool