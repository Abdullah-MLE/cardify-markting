from pydantic import BaseModel, Field, ConfigDict

# Database Models (match Supabase schema)

class Company(BaseModel):
    """companies table"""
    id: int | None = Field(default=None)
    created_at: str | None = Field(default=None)
    company_name: str
    industry: str | None = None
    description: str | None = None
    mission_and_goal: str | None = None
    brand_tone: str | None = None
    target_audience: str | None = None
    language_and_locale: str | None = None
    constraints: str | None = None
    is_character: bool | None = Field(default=False)
    main_character_name: str | None = None
    main_character_constraints: str | None = None
    main_character_image_url: str | None = None
    visual_constraints: str | None = None
    visual_style: str | None = None
    brand_color: str | None = None
    logo_url: str | None = None
    website_url: str | None = None
    social_media_username: str | None = None
    facebook_url: str | None = None
    x_url: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    tiktok_url: str | None = None

class User(BaseModel):
    """users table"""
    id: int | None = Field(default=None)
    created_at: str | None = Field(default=None)
    username: str
    password: str
    role: str | None = Field(default="company_user")
    company_id: int | None = None

class Campaign(BaseModel):
    """campaigns table (formerly weekly_plans)"""
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = Field(default=None)
    created_at: str | None = Field(default=None)
    company_id: int
    start_date: str | None = None
    end_date: str | None = None
    plan_title: str
    status: str | None = Field(default="draft")
    ai_plan: str | None = Field(default=None, alias="plan_content")

# Backward compatibility alias
WeeklyPlan = Campaign

class Content(BaseModel):
    """content table (Unified)"""
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = Field(default=None)
    created_at: str | None = Field(default=None)
    company_id: int
    campaign_id: int | None = Field(default=None, alias="week_id")
    content_type: str = Field(default="post", description="'post', 'story', 'carousel'")
    publish_date: str | None = None
    publish_time: str | None = None
    publish_day: str | None = Field(default="")
    status: str = "planned"
    
    # JSONB fields - accepting single strings/bools to prevent validation errors for old data
    h1: list[str] | str | None = Field(default_factory=list, description="Headlines or Text (JSONB)")
    caption: str | None = Field(default="")
    post_images: list[str] | str | None = Field(default_factory=list, description="Image URLs (JSONB)")
    post_idea: list[str] | str | None = Field(default_factory=list, description="Visual Prompts (JSONB)")
    use_character: list[bool] | bool | None = Field(default_factory=list, description="Character Usage (JSONB)")

class Template(BaseModel):
    """templates table"""
    id: int | None = Field(default=None)
    created_at: str | None = Field(default=None)
    company_id: int
    title: str | None = None
    template_url: str | None = Field(default=None)
    template_info: str | None = None
    template_constraints: str | None = Field(default=None)
    source_post_url: str | None = Field(default=None)
    is_source_same_company: bool = Field(default=False)
    aspect_ratio: str | None = Field(default=None)
