"""
High-level AI service. Connects old Python prompt system to the GeminiWrapper.
"""

import logging
from typing import Any, Dict, List, Optional

from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams
import services.prompts as prompts

logger = logging.getLogger("AIService")

class AIService:
    """High-level orchestrator that connects python prompts to the GeminiWrapper."""

    def __init__(self, wrapper: Optional[GeminiWrapper] = None) -> None:
        self.wrapper = wrapper or GeminiWrapper()

    def execute_text_skill(
        self,
        skill_name: str,
        context: Dict[str, Any],
        response_schema: Any = None,
        media: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        
        system_prompt = ""
        user_prompt = ""
        
        if skill_name == "generate_post":
            system_prompt = prompts.single_post_system_prompt()
            user_prompt = prompts.single_post_user_prompt(
                context.get("headline", ""),
                context.get("notes", ""),
                context.get("company", {})
            )
        elif skill_name == "generate_story":
            system_prompt = prompts.single_post_system_prompt()
            user_prompt = prompts.single_post_user_prompt(
                context.get("headline", ""),
                context.get("notes", ""),
                context.get("company", {})
            )
        elif skill_name == "generate_carousel":
            system_prompt = prompts.carousel_gen_system_prompt()
            user_prompt = prompts.carousel_gen_user_prompt(
                context.get("headline", ""),
                context.get("notes", "")
            )
        elif skill_name == "generate_day_content":
            system_prompt = prompts.day_content_system_prompt()
            user_prompt = prompts.day_content_user_prompt(
                context.get("weekly_plan", {}),
                context.get("company", {}),
                context.get("date", ""),
                context.get("day_name", ""),
                context.get("day_order", ""),
                context.get("notes", "")
            )
        elif skill_name == "analyze_company":
            system_prompt = prompts.extract_company_system_prompt()
            user_prompt = prompts.extract_company_user_prompt(
                context.get("source_text", "")
            )
        elif skill_name == "create_weekly_plan":
            system_prompt = prompts.create_weekly_plan_system_prompt()
            user_prompt = prompts.create_weekly_plan_user_prompt(
                context.get("company", {}),
                context.get("campaign", {}),
                context.get("start_date", ""),
                context.get("notes", "")
            )
        elif skill_name == "analyze_template":
            system_prompt = prompts.template_analysis_system_prompt()
            user_prompt = prompts.template_analysis_user_prompt(
                context.get("company", {})
            )
        else:
            logger.warning(f"Unknown text skill: {skill_name}")
            system_prompt = "You are a helpful assistant."
            user_prompt = str(context)

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
            logger.error(f"Skill '{skill_name}' failed: {result.get('error')}")

        return result

    def execute_image_skill(
        self,
        skill_name: str,
        context: Dict[str, Any],
        media: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
    ) -> Dict[str, Any]:
        
        system_prompt = ""
        user_prompt = ""
        
        if skill_name == "generate_image":
            system_prompt = prompts.image_gen_system_prompt()
            user_prompt = prompts.image_gen_user_prompt(
                context.get("prompt", ""),
                context.get("headline", ""),
                context.get("post_idea", ""),
                context.get("template_constraints", "")
            )
        elif skill_name == "edit_image":
            system_prompt = prompts.image_edit_system_prompt()
            user_prompt = prompts.image_edit_user_prompt(
                context.get("post_idea", ""),
                context.get("notes", "")
            )
        elif skill_name == "generate_template":
            if "notes" in context:
                system_prompt = prompts.template_edit_system_prompt()
                user_prompt = prompts.template_edit_user_prompt(
                    context.get("notes", "")
                )
            else:
                system_prompt = prompts.template_creation_from_prompt_system_prompt()
                user_prompt = prompts.template_creation_from_prompt_user_prompt(
                    context.get("user_request", ""),
                    context.get("company", {})
                )
        else:
            logger.warning(f"Unknown image skill: {skill_name}")
            system_prompt = "You are a graphic designer."
            user_prompt = str(context)

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
