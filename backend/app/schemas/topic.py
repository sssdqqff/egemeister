from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    number: int = Field(..., gt=0, description="Номер задания КИМ")
    name: str = Field(..., min_length=3, max_length=50, description="Название темы")
    slug: str = Field(..., min_length=3, max_length=100, description="Уникальный идентификатор темы")
    description: str | None = Field(None, min_length=10, max_length=500)
    subject_id: int = Field(..., gt=0, description="ID предмета")
    is_active: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)


class TopicUpdate(BaseModel):
    number: int | None = Field(None, gt=0)
    name: str | None = Field(None, min_length=3, max_length=50)
    slug: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, min_length=10, max_length=500)
    is_active: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class TopicResponse(BaseModel):
    id: int
    number: int
    name: str
    slug: str
    description: str | None
    is_active: bool
    subject_id: int

    model_config = ConfigDict(from_attributes=True)