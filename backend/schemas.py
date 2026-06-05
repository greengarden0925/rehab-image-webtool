from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    modes: List[Literal["a", "b"]] = Field(default=["a", "b"])
    max_iterations: int = Field(default=3, ge=1, le=3)
    locale: Literal["zh-TW", "en"] = Field(default="zh-TW")


class ValidateKeyResponse(BaseModel):
    valid: bool
    message: Optional[str] = None
