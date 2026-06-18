from pydantic import BaseModel
from typing import List


class GeminiConfig(BaseModel):
    # Text Generation Models
    default_text_model: str = "gemini-3.5-flash"
    text_fallback_models: List[str] = ["gemini-3.5-flash"]

    # Image Generation Models
    default_image_model: str = "imagen-3.0-generate-001"
    image_models: List[str] = ["imagen-3.0-generate-001"]

    # Image Output Settings
    default_output_image_aspect_ratio: str = "1:1"

    # Image Processing
    default_image_max_dimension: int = 500
    default_media_resolution: str = "MEDIA_RESOLUTION_UNSPECIFIED"

    # Retry Settings
    retry_delay_seconds: float = 2.0
    text_max_retries_per_model: int = 2
    text_overall_max_retries: int = 10
    image_max_retries_per_model: int = 2
    image_overall_max_retries: int = 5

    # Defaults
    default_system_instruction: str = "You are a helpful assistant"
    default_response_mime_type: str = "application/json"


config = GeminiConfig()
