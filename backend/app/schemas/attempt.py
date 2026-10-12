from pydantic import BaseModel, ConfigDict, Field, field_validator

class AttemptCreate(BaseModel):
    task_id: int = Field(..., gt=0, description="ID of the task")
    session_id: int | None = Field(None, gt=0, description="Session ID (optional for solo mode)")
    user_answer: str = Field(..., min_length=1, description="User's answer")

    model_config = ConfigDict(str_strip_whitespace=True)


class AttemptResponse(BaseModel):
    id: int = Field(..., description="Attempt ID")
    task_id: int = Field(..., description="Task ID")
    session_id: int | None = Field(None, description="Session ID")
    user_answer: str = Field(..., description="User's answer")
    is_correct: bool = Field(..., description="Whether answer is correct")

    model_config = ConfigDict(from_attributes=True)