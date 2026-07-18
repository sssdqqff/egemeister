from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    condition: str = Field(..., min_length=10, description="Task condition")
    answer: str = Field(..., description="Correct answer")
    difficulty: str = Field(default="medium", description="easy, medium, hard")
    topic_id: int = Field(..., description="Topic ID")


class TaskUpdate(BaseModel):
    condition: str | None = Field(None, min_length=10)
    answer: str | None = Field(None)
    difficulty: str | None = Field(None)


class TaskResponse(BaseModel):
    id: int = Field(..., description="Task unique identifier")
    condition: str = Field(..., description="Task condition")
    difficulty: str = Field(..., description="Difficulty level")
    is_active: bool = Field(..., description="Is task active")
    topic_id: int = Field(..., description="Topic ID")

    model_config = ConfigDict(from_attributes=True)