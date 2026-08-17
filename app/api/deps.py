"""Dependency Injection for API routes."""
from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper, init_gemini_client
from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.crud import (
    company_crud,
    template_crud,
    weekly_plan_crud,
    content_crud
)
from app.services.scraper_service import ScraperService
from app.services.base_service import BaseService
from app.services.weekly_plan_service import WeeklyPlanService
from app.services.content_service import ContentService
from app.services.template_service import TemplateService

# Initialize shared infrastructure dependencies
gemini_client = init_gemini_client()
gemini_wrapper = GeminiWrapper(gemini_client)
supabase_crud = SupabaseCRUD()

# Initialize AI domain services
base_service = BaseService(gemini_wrapper, supabase_crud)
scraper_service = ScraperService(gemini_wrapper, supabase_crud)
weekly_plan_service = WeeklyPlanService(gemini_wrapper, supabase_crud)
content_service = ContentService(gemini_wrapper, supabase_crud)
template_service = TemplateService(gemini_wrapper, supabase_crud)

__all__ = [
    "gemini_client",
    "gemini_wrapper",
    "supabase_crud",
    "company_crud",
    "template_crud",
    "weekly_plan_crud",
    "content_crud",
    "base_service",
    "scraper_service",
    "weekly_plan_service",
    "content_service",
    "template_service",
]
