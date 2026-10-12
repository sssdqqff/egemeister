from pydantic import BaseModel, ConfigDict, Field

class PrototypeCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Prototype name")
    code: str = Field(..., min_length=1, max_length=20, description="Unique prototype code")
    description: str | None = Field(None, max_length=500, description="Prototype description")
    exam_number: int = Field(..., gt=0, description="Exam task number")

    model_config = ConfigDict(str_strip_whitespace=True)


class PrototypeUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    code: str | None = Field(None, min_length=1, max_length=20)
    description: str | None = Field(None, max_length=500)
    exam_number: int | None = Field(None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class PrototypeResponse(BaseModel):
    id: int
    name: str
    code: str
    description: str | None
    exam_number: int

    model_config = ConfigDict(from_attributes=True)