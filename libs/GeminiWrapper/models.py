from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InputParams(BaseModel):
    prompt: Optional[str] = None
    media: Optional[List[str]] = None
    model: Optional[str] = None
    processed_image_size: Optional[int] = None
    media_resolution: Optional[str] = None
    system_instruction: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class TextParams(BaseModel):
    response_schema: Any = None
    response_mime_type: Optional[str] = None
    tools: Optional[List[Any]] = None
    tool_config: Any = None

    class Config:
        arbitrary_types_allowed = True


class ImageParams(BaseModel):
    output_image_aspect_ratio: Optional[str] = None
    output_image_size: Optional[str] = None


class OutputResult(BaseModel):
    content: Any = None
    model_used: str = ""
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"input": 0, "output": 0})
    success: bool = False
    error: Optional[str] = None
    retry_attempts: int = 0
    error_log: List[str] = Field(default_factory=list)
    raw_response: Any = None

    class Config:
        arbitrary_types_allowed = True
