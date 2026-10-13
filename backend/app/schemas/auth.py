from pydantic import BaseModel, ConfigDict, Field


class BotLoginCodeRequest(BaseModel):
    telegram_id: int = Field(..., gt=0)
    first_name: str | None = Field(None, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)


class BotLoginCodeResponse(BaseModel):
    code: str
    expires_in: int


class CodeExchangeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=12, pattern=r"^\d+$")

    model_config = ConfigDict(str_strip_whitespace=True)