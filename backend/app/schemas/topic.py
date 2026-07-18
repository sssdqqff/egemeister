from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Topic name")
    description: str = Field(..., min_length=10, max_length=500, description="Topic description")
    subject_id: int = Field(..., description="ID of the subject this topic belongs to")
    is_active: bool = Field(default=True, description="Indicates if the topic is active")


class TopicUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, min_length=10, max_length=500)
    is_active: bool | None = Field(None, description="Indicates if the topic is active")


class TopicResponse(BaseModel):
    id: int = Field(..., description="Topic unique identifier")
    name: str = Field(..., min_length=3, max_length=50, description="Topic name")
    description: str = Field(..., min_length=10, max_length=500, description="Topic description")
    is_active: bool = Field(..., description="Indicates if the topic is active")
    subject_id: int = Field(..., description="ID of the subject this topic belongs to")

    model_config = ConfigDict(from_attributes=True)