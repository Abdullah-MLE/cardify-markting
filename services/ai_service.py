"""
Pure AI Execution Service
Provides a clean wrapper to the GeminiWrapper for executing predefined prompt configurations.
"""

import logging
from typing import Any, Dict, List, Optional

from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams

logger = logging.getLogger("AIService")

class AIService:
    """A purely functional executor that passes prompts to Gemini without containing business logic."""

    def __init__(self, wrapper: Optional[GeminiWrapper] = None) -> None:
        self.wrapper = wrapper or GeminiWrapper()

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Any = None,
        media: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Executes a text generation task given raw prompts."""
        
        input_params = InputParams(
            prompt=user_prompt,
            system_instruction=system_prompt,
            media=media,
        )

        text_params: Optional[TextParams] = None
        if response_schema is not None:
            text_params = TextParams(
                response_schema=response_schema,
                response_mime_type="application/json",
            )

        result = self.wrapper.generate_text(
            input_params=input_params,
            text_params=text_params,
        )

        if not result.get("success"):
            logger.error(f"Text generation failed: {result.get('error')}")

        return result

    def generate_image(
        self,
        system_prompt: str,
        user_prompt: str,
        media: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
    ) -> Dict[str, Any]:
        """Executes an image generation task given raw prompts."""
        
        input_params = InputParams(
            prompt=user_prompt,
            system_instruction=system_prompt,
            media=media,
        )
        
        image_params = ImageParams(output_image_aspect_ratio=aspect_ratio)

        result = self.wrapper.generate_image(
            input_params=input_params,
            image_params=image_params,
        )

        if not result.get("success"):
            logger.error(f"Image generation failed: {result.get('error')}")

        return result


# Module-level singleton
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Return a process-wide singleton AIService instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
