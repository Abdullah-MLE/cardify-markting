from app.services.base_service import BaseService
from app.crud import company_crud, template_crud
from app.schemas.ai_models import TempletAnalysis
from app.core.prompts import (
    template_analysis_system_prompt,
    template_analysis_user_prompt,
    template_generation_system_prompt,
    template_generation_user_prompt,
    template_constraint_system_prompt,
    template_constraint_user_prompt,
    template_creation_from_prompt_system_prompt,
    template_creation_from_prompt_user_prompt,
    template_edit_system_prompt
)


class TemplateService(BaseService):

    def analyze_template(self, post_url: str, company_id: int) -> TempletAnalysis:
        """Analyzes a post image to extract template structure and brand info."""
        company = company_crud.get_by_id(self.supabase_crud, company_id)
        logo_url = company.logo_url or ""
        
        system_prompt = template_analysis_system_prompt()
        user_prompt = template_analysis_user_prompt(company)
        media = [post_url, logo_url] if logo_url else [post_url]
        
        return self.generate_text(user_prompt, system_prompt, TempletAnalysis, media=media)

    def create_template_from_image(self, analysis: TempletAnalysis, company_id: int, post_url: str, user_instructions: str = None) -> str:
        """Generates a reusable template image based on the analysis of an existing post."""
        company = company_crud.get_by_id(self.supabase_crud, company_id)

        system_prompt = template_generation_system_prompt()
        user_prompt = template_generation_user_prompt(analysis)
        
        if user_instructions:
            user_prompt += f"\n\nAdditional User Instructions: {user_instructions}"
            
        media = [post_url, company.logo_url] if company.logo_url else [post_url]
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=media, aspect_ratio=analysis.aspect_ratio)
        return self.upload_image(image_bytes, f"template-{company_id}.png")

    def create_template_from_prompt(self, company_id: int, prompt: str) -> str:
        """Generates a template based on user prompt and company info."""
        company = company_crud.get_by_id(self.supabase_crud, company_id)
        
        system_prompt = template_creation_from_prompt_system_prompt()
        user_prompt = template_creation_from_prompt_user_prompt(company, prompt)
        
        media = [company.logo_url] if company.logo_url else None
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=media, aspect_ratio="3:4")
        return self.upload_image(image_bytes, f"template-prompt-{company_id}.png")

    def generate_template_constraints(self, company_id: int, post_url: str, template_url: str) -> str:
        """Generates strict usage constraints by comparing the original post and the new template."""
        company = company_crud.get_by_id(self.supabase_crud, company_id)
        
        system_prompt = template_constraint_system_prompt()
        user_prompt = template_constraint_user_prompt(company)
        
        result = self.generate_text(user_prompt, system_prompt, media=[post_url, template_url])
        return result if result else "Follow general branding guidelines."

    def edit_template(self, template_id: int, notes: str) -> str:
        """Edits an existing template based on user instructions."""
        template = template_crud.get_by_id(self.supabase_crud, template_id)
        
        system_prompt = template_edit_system_prompt()
        
        image_bytes = self.generate_image(notes, system_prompt, media=[template.template_url], aspect_ratio=template.aspect_ratio or "3:4")
        return self.upload_image(image_bytes, f"template-{template_id}-edited.png")