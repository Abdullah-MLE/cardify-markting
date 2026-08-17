from pydantic import BaseModel, Field, ConfigDict


class CompanyBase(BaseModel):
    """Common fields for Company"""
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


class CompanyCreate(CompanyBase):
    """Schema for creating a new Company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating an existing Company (all fields optional)"""
    company_name: str | None = None
    industry: str | None = None
    description: str | None = None
    mission_and_goal: str | None = None
    brand_tone: str | None = None
    target_audience: str | None = None
    language_and_locale: str | None = None
    constraints: str | None = None
    is_character: bool | None = None
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


class CompanyResponse(CompanyBase):
    """Schema for Company response returned to user"""
    id: int
    created_at: str | None = None

    model_config = ConfigDict(from_attributes=True)
