"""
Template Service
Handles AI-driven template creation, analysis, and editing.
Adapted from old/app/services/template_service.py.
"""
from services.base_service import BaseService
from schemas.db_models import Template
from schemas.ai_models import TemplateAnalysis
from services.prompts.template_prompts import (
    template_analysis_system_prompt,
    template_analysis_user_prompt,
    template_generation_system_prompt,
    template_generation_user_prompt,
    template_constraint_system_prompt,
    template_constraint_user_prompt,
    template_creation_from_prompt_system_prompt,
    template_creation_from_prompt_user_prompt,
    template_edit_system_prompt,
)


class TemplateService(BaseService):
    """Service for template creation, analysis, and editing."""

    # ─── Create from Image ────────────────────────────────────────────────────

    def analyze_template(self, post_url: str, company_id: int) -> TemplateAnalysis:
        """Analyze an existing post image to extract template structure."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()
        logo_url = company_dict.get("logo_url")

        sys_p = template_analysis_system_prompt()
        usr_p = template_analysis_user_prompt(company_dict)
        media = [post_url, logo_url] if logo_url else [post_url]

        return self.generate_text(usr_p, sys_p, TemplateAnalysis, media=media)

    def create_template_from_image(
        self,
        company_id: int,
        post_url: str,
        user_instructions: str = None,
    ) -> bytes:
        """Generate a blank reusable template image from an original design directly."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()
        logo_url = company_dict.get("logo_url")
        company_name = company_dict.get("company_name", "the company")

        # Simplified system prompt
        sys_p = f"Modify the provided template design to match the company '{company_name}'. Change the logo to the provided logo. Keep all other layout and background structures exactly as they are. Make the template clean and empty of any temporary texts."
        
        # User prompt
        usr_p = f"Instructions: {user_instructions}" if user_instructions else "Generate a clean blank template for this brand."

        media = [post_url]
        if logo_url:
            media.append(logo_url)
        else:
            self.logger.warning("No logo_url found for company during template extraction!")

        aspect_ratio = "1:1"

        return self.generate_image(usr_p, sys_p, media=media, aspect_ratio=aspect_ratio)

    def generate_template_constraints(
        self, company_id: int, post_url: str, template_url: str
    ) -> str:
        """Generate usage constraints for a template by comparing source and generated."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()

        sys_p = template_constraint_system_prompt()
        usr_p = template_constraint_user_prompt(company_dict)

        result = self.generate_text(usr_p, sys_p, media=[post_url, template_url])
        return result or "Follow general branding guidelines."

    # ─── Create from Prompt ───────────────────────────────────────────────────

    def create_template_from_prompt(
        self, company_id: int, prompt: str, aspect_ratio: str = "1:1"
    ) -> bytes:
        """Generate a template from a user text prompt."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()
        logo_url = company_dict.get("logo_url")

        sys_p = template_creation_from_prompt_system_prompt()
        usr_p = template_creation_from_prompt_user_prompt(company_dict, prompt)
        media = [logo_url] if logo_url else None

        return self.generate_image(usr_p, sys_p, media=media, aspect_ratio=aspect_ratio)

    def modify_template(
        self,
        template_id: int,
        mod_prompt: str,
        company_id: int,
    ) -> bytes:
        """Edit an existing template via AI and return new image bytes."""
        template = self.get_template(template_id)
        company = self.get_company(company_id)
        company_dict = company.model_dump()

        original_name = template.template_info or "Template"
        combined_prompt = f"{original_name}\n\nModification Request: {mod_prompt}"
        aspect_ratio = template.aspect_ratio or "1:1"

        sys_p = template_creation_from_prompt_system_prompt()
        usr_p = template_creation_from_prompt_user_prompt(company_dict, combined_prompt)
        media = [template.template_url] if template.template_url else None

        return self.generate_image(usr_p, sys_p, media=media, aspect_ratio=aspect_ratio)

    def edit_template(self, template_id: int, notes: str) -> bytes:
        """Edit an existing template using an edit prompt."""
        template = self.get_template(template_id)
        sys_p = template_edit_system_prompt()
        aspect_ratio = template.aspect_ratio or "1:1"
        media = [template.template_url] if template.template_url else None

        return self.generate_image(notes, sys_p, media=media, aspect_ratio=aspect_ratio)


# Module-level singleton
_template_service: TemplateService | None = None


def get_template_service() -> TemplateService:
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
