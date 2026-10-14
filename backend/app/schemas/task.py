from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    condition: str = Field(..., min_length=10, description="Task condition")
    answer: str = Field(..., min_length=1, description="Correct answer")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Difficulty level")
    topic_id: int = Field(..., gt=0, description="Topic ID")
    prototype_id: int = Field(..., gt=0, description="Prototype ID")

    model_config = ConfigDict(str_strip_whitespace=True)


class TaskUpdate(BaseModel):
    condition: str | None = Field(None, min_length=10)
    answer: str | None = Field(None, min_length=1)
    difficulty: Literal["easy", "medium", "hard"] | None = Field(None)
    topic_id: int | None = Field(None, gt=0, description="Topic ID")
    prototype_id: int | None = Field(None, gt=0, description="Prototype ID")

    model_config = ConfigDict(str_strip_whitespace=True)


class TaskResponse(BaseModel):
    id: int
    condition: str
    difficulty: Literal["easy", "medium", "hard"]
    is_active: bool
    topic_id: int
    prototype_id: int

    model_config = ConfigDict(from_attributes=True)
