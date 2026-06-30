from pydantic import BaseModel, Field
from typing import Optional, List


# ─── Database Models (match Supabase schema) ─────────────────────────────────

class Company(BaseModel):
    """companies table"""
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    mission_and_goal: Optional[str] = None
    brand_tone: Optional[str] = None
    target_audience: Optional[str] = None
    language_and_locale: Optional[str] = None
    constraints: Optional[str] = None
    is_character: Optional[bool] = False
    main_character_name: Optional[str] = None
    main_character_constraints: Optional[str] = None
    main_character_image_url: Optional[str] = None
    visual_constraints: Optional[str] = None
    visual_style: Optional[str] = None
    brand_color: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    social_media_username: Optional[str] = None
    facebook_url: Optional[str] = None
    x_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    tiktok_url: Optional[str] = None


class Campaign(BaseModel):
    """campaigns table"""
    company_id: int
    plan_title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    plan_content: Optional[str] = None
    status: Optional[str] = "draft"
    ai_plan: Optional[str] = None


class Content(BaseModel):
    """content table"""
    id: Optional[int] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    company_id: int
    campaign_id: Optional[int] = Field(default=None)
    content_type: str = Field(default="post", description="'post', 'story', 'carousel'")
    publish_date: Optional[str] = None
    publish_time: Optional[str] = None
    publish_day: Optional[str] = Field(default="")
    status: str = "planned"
    h1: Optional[List[str]] = Field(default_factory=list, description="Headlines (JSONB)")
    caption: Optional[str] = Field(default="")
    post_images: Optional[List[str]] = Field(default_factory=list, description="Image URLs (JSONB)")
    post_idea: Optional[object] = Field(default=None, description="Visual Prompts (JSONB)")
    use_character: Optional[object] = Field(default=None, description="Character Usage (JSONB)")


class Template(BaseModel):
    """templates table"""
    id: Optional[int] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    company_id: int
    template_url: Optional[str] = Field(default=None)
    template_info: Optional[str] = Field(default=None)
    template_constraints: Optional[str] = Field(default=None)
    source_post_url: Optional[str] = Field(default=None)
    is_source_same_company: bool = Field(default=False)
    aspect_ratio: Optional[str] = Field(default=None)
