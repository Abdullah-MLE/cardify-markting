"""Dependency Injection for API routes."""
from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper, init_gemini_client
from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.services.scraper_service import ScraperService
from app.services.base_service import BaseService
from app.services.weekly_plan_service import WeeklyPlanService
from app.services.content_service import ContentService
from app.services.template_service import TemplateService

# Initialize shared dependencies
gemini_client = init_gemini_client()
gemini_wrapper = GeminiWrapper(gemini_client)
supabase_crud = SupabaseCRUD()

# Initialize services
base_service = BaseService(gemini_wrapper, supabase_crud)
scraper_service = ScraperService(gemini_wrapper, supabase_crud)
weekly_plan_service = WeeklyPlanService(gemini_wrapper, supabase_crud)
content_service = ContentService(gemini_wrapper, supabase_crud)
template_service = TemplateService(gemini_wrapper, supabase_crud)
