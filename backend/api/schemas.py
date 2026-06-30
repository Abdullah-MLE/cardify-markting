"""API Schemas for Request/Response handling in FastAPI."""
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

# --- Companies ---
class CompanyCreate(BaseModel):
    company_name: str
    industry: str
    description: Optional[str] = None
    # Add other fields flexibly using dict if needed

class CompanyUpdate(BaseModel):
    data: Dict[str, Any]

class UserCreate(BaseModel):
    company_id: int
    username: str
    password: str
    role: str

class ScrapeRequest(BaseModel):
    company_id: int
    url: str

class EditProfileRequest(BaseModel):
    company_id: int
    company_data: Dict[str, Any]
    notes: str

# --- Campaigns ---
class CampaignCreate(BaseModel):
    company_id: int
    plan_title: str
    start_date: str
    end_date: str
    status: str = "draft"

class CampaignUpdate(BaseModel):
    data: Dict[str, Any]

class GeneratePlanRequest(BaseModel):
    campaign_id: int
    company_id: int
    camp_data: Dict[str, Any]
    user_brief: str

class GenerateContentRequest(BaseModel):
    campaign_id: int
    company_id: int
    camp_data: Dict[str, Any]
    ai_plan_text: str
    user_brief: str

# --- Content ---
class ContentCreate(BaseModel):
    data: Dict[str, Any]

class SinglePostRequest(BaseModel):
    company_id: int
    h1: str
    notes: str = ""
    campaign_id: Optional[int] = None
    publish_date: Optional[str] = None
    publish_time: Optional[str] = None

class GenerateMediaRequest(BaseModel):
    template_id: Optional[int] = None
    user_instructions: Optional[str] = None

class EditMediaRequest(BaseModel):
    notes: str
    slide_index: Optional[int] = None

# --- Templates ---
class AnalyzeTemplateRequest(BaseModel):
    post_url: str
    company_id: int

class CreateFromImageRequest(BaseModel):
    post_url: str
    company_id: int
    instructions: Optional[str] = None

class ExtractTemplateRequest(BaseModel):
    analysis: Dict[str, Any]
    company_id: int
    post_url: str
    instructions: Optional[str] = None

class PromptTemplateRequest(BaseModel):
    company_id: int
    prompt: str
    aspect_ratio: str = "1:1"

class EditTemplateRequest(BaseModel):
    notes: str
