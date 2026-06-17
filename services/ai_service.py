"""
High-level AI service. Connects skills (Markdown) to the GeminiWrapper.

The calling code never touches prompts directly — it says:
    ai_service.execute_text_skill("generate_post", context={...}, response_schema=SinglePostGeneration)
and the loader does the rest.
"""

import logging
from typing import Any, Dict, List, Optional

from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams
from services.prompt_loader import PromptLoader

logger = logging.getLogger("AIService")


class AIService:
    """High-level orchestrator that connects skills to the GeminiWrapper."""

    def __init__(self, wrapper: Optional[GeminiWrapper] = None) -> None:
        self.wrapper = wrapper or GeminiWrapper()
        self.loader = PromptLoader()

    # ------------------------------------------------------------------
    # Text skills (output: JSON matching a Pydantic model)
    # ------------------------------------------------------------------

    def execute_text_skill(
        self,
        skill_name: str,
        context: Dict[str, Any],
        response_schema: Any = None,
        media: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute a text-generation skill and return the Gemini result dict.

        Parameters
        ----------
        skill_name:
            Directory name under `skills/`.
        context:
            Variables for the user_context.md Jinja2 template.
        response_schema:
            Pydantic model class to use as the response schema (forces JSON).
        media:
            Optional list of media URLs to include in the prompt (for image
            inputs in multimodal skills like `analyze_template`).
        """
        skill = self.loader.load_skill(skill_name, context)

        input_params = InputParams(
            prompt=skill["user_prompt"],
            system_instruction=skill["system_prompt"],
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
            logger.error(f"Skill '{skill_name}' failed: {result.get('error')}")

        return result

    # ------------------------------------------------------------------
    # Image skills (output: image bytes)
    # ------------------------------------------------------------------

    def execute_image_skill(
        self,
        skill_name: str,
        context: Dict[str, Any],
        media: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
    ) -> Dict[str, Any]:
        """Execute an image-generation skill and return the Gemini result dict."""
        skill = self.loader.load_skill(skill_name, context)

        input_params = InputParams(
            prompt=skill["user_prompt"],
            system_instruction=skill["system_prompt"],
            media=media,
        )
        image_params = ImageParams(output_image_aspect_ratio=aspect_ratio)

        result = self.wrapper.generate_image(
            input_params=input_params,
            image_params=image_params,
        )

        if not result.get("success"):
            logger.error(f"Image skill '{skill_name}' failed: {result.get('error')}")

        return result


# Module-level singleton
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Return a process-wide singleton AIService instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
