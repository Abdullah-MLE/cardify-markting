from pydantic import BaseModel, Field, ConfigDict


class TemplateBase(BaseModel):
    """Common fields for Template"""
    company_id: int
    title: str | None = None
    template_url: str | None = Field(default=None)
    template_info: str | None = None
    template_constraints: str | None = Field(default=None)
    source_post_url: str | None = Field(default=None)
    is_source_same_company: bool = Field(default=False)
    aspect_ratio: str | None = Field(default=None)


class TemplateCreate(TemplateBase):
    """Schema for creating a new Template"""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating an existing Template (all fields optional)"""
    company_id: int | None = None
    title: str | None = None
    template_url: str | None = None
    template_info: str | None = None
    template_constraints: str | None = None
    source_post_url: str | None = None
    is_source_same_company: bool | None = None
    aspect_ratio: str | None = None


class TemplateResponse(TemplateBase):
    """Schema for Template response returned to user"""
    id: int
    created_at: str | None = None

    model_config = ConfigDict(from_attributes=True)
