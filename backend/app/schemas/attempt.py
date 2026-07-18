from pydantic import BaseModel, Field, ConfigDict


class AttemptCreate(BaseModel):
    task_id: int = Field(..., description="ID of the task")
    session_id: int | None = Field(None, description="Session ID (optional for solo mode)")
    user_answer: str = Field(..., description="User's answer")


class AttemptResponse(BaseModel):
    id: int = Field(..., description="Attempt ID")
    task_id: int = Field(..., description="Task ID")
    session_id: int | None = Field(None, description="Session ID")
    user_answer: str = Field(..., description="User's answer")
    is_correct: bool = Field(..., description="Whether answer is correct")

    model_config = ConfigDict(from_attributes=True)