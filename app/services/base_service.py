from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams
from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.db_models import Company, WeeklyPlan, Template, Content


class BaseService:
    """Base class with shared helpers for all services."""
    
    def __init__(self, gemini_wrapper: GeminiWrapper, supabase_crud: SupabaseCRUD):
        self.gemini_wrapper = gemini_wrapper
        self.supabase_crud = supabase_crud

    # ENTITY GETTERS
    def get_company(self, company_id: int) -> Company:
        data = self.supabase_crud.get_row_by_id("companies", company_id)
        if not data:
            raise ValueError(f"Company {company_id} not found.")
        return Company(**data)

    def get_weekly_plan(self, weekly_plan_id: int) -> WeeklyPlan:
        data = self.supabase_crud.get_row_by_id("campaigns", weekly_plan_id)
        if not data:
            raise ValueError(f"Plan {weekly_plan_id} not found.")
        return WeeklyPlan(**data)

    def get_template(self, template_id: int) -> Template:
        data = self.supabase_crud.get_row_by_id("templates", template_id)
        if not data:
            raise ValueError(f"Template {template_id} not found.")
        return Template(**data)

    def get_content(self, content_id: int) -> Content:
        data = self.supabase_crud.get_row_by_id("content", content_id)
        if not data:
            raise ValueError(f"Content {content_id} not found.")
        return Content(**data)

    # ENTITY INSERTERS
    def insert_company(self, company: Company) -> int:
        data = company.model_dump(exclude_none=True)
        res = self.supabase_crud.insert_row("companies", data)
        return res.get("id")

    def insert_template(self, template: Template) -> int:
        data = template.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = self.supabase_crud.insert_row("templates", data)
        return res.get("id")

    def insert_weekly_plan(self, plan: WeeklyPlan) -> int:
        if plan.ai_plan and (plan.status == "draft" or not plan.status):
            plan.status = "planned"
        data = plan.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = self.supabase_crud.insert_row("campaigns", data)
        return res.get("id")

    def insert_content(self, content: Content) -> int:
        if not content.post_images or all(url == "" for url in content.post_images):
            content.status = "pending_images"
        else:
            content.status = "completed"
        data = content.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = self.supabase_crud.insert_row("content", data)
        return res.get("id")

    # ENTITY UPDATERS
    def update_company(self, company_id: int, company: Company):
        data = company.model_dump(exclude_none=True, exclude={"id", "created_at"})
        return self.supabase_crud.update_row("companies", data, company_id)

    def update_template(self, template_id: int, template: Template):
        data = template.model_dump(exclude_none=True, exclude={"id", "created_at"})
        return self.supabase_crud.update_row("templates", data, template_id)

    def update_weekly_plan(self, plan_id: int, plan: WeeklyPlan):
        if plan.ai_plan and (plan.status == "draft" or not plan.status):
            plan.status = "planned"
        data = plan.model_dump(exclude_none=True, exclude={"id", "created_at"})
        return self.supabase_crud.update_row("campaigns", data, plan_id)

    def update_content(self, content_id: int, content: Content):
        if not content.post_images or all(url == "" for url in content.post_images):
            content.status = "pending_images"
        else:
            content.status = "completed"
        data = content.model_dump(exclude_none=True, exclude={"id", "created_at"})
        return self.supabase_crud.update_row("content", data, content_id)



    # TEXT GENERATION
    def generate_text(self, prompt: str, system_instruction: str, response_schema=None, media: list = None):
        """Generate text. If response_schema is provided, returns structured JSON. Otherwise plain text."""
        input_params = InputParams(prompt=prompt, system_instruction=system_instruction, media=media)
        
        if response_schema:
            text_params = TextParams(response_schema=response_schema, response_mime_type='application/json')
            result = self.gemini_wrapper.generate_text(input_params=input_params, text_params=text_params)
        else:
            result = self.gemini_wrapper.generate_text(input_params=input_params)
        
        if not result.get("success"):
            raise Exception(f"AI generation failed: {result.get('error')}")
        return result.get("content")

    # IMAGE GENERATION
    def generate_image(self, prompt: str, system_instruction: str, media: list = None, aspect_ratio: str = "3:4") -> bytes:
        input_params = InputParams(prompt=prompt, system_instruction=system_instruction, media=media)
        image_params = ImageParams(output_image_aspect_ratio=aspect_ratio)
        result = self.gemini_wrapper.generate_image(input_params=input_params, image_params=image_params)
        if not result.get("success"):
            raise Exception(f"Image generation failed: {result.get('error')}")
        return result.get("content")

    def upload_image(self, image_bytes: bytes, filename: str) -> str:
        return self.supabase_crud.upload_image(image_bytes, filename)
