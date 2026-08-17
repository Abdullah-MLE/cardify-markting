from pydantic import BaseModel, Field, ConfigDict


class ContentBase(BaseModel):
    """Common fields for Content"""
    model_config = ConfigDict(populate_by_name=True)

    company_id: int
    campaign_id: int | None = Field(default=None, alias="week_id")
    content_type: str = Field(default="post", description="'post', 'story', 'carousel'")
    publish_date: str | None = None
    publish_time: str | None = None
    publish_day: str | None = Field(default="")
    status: str = "planned"

    # JSONB fields
    h1: list[str] | str | None = Field(default_factory=list, description="Headlines or Text (JSONB)")
    caption: str | None = Field(default="")
    post_images: list[str] | str | None = Field(default_factory=list, description="Image URLs (JSONB)")
    post_idea: list[str] | str | None = Field(default_factory=list, description="Visual Prompts (JSONB)")
    use_character: list[bool] | bool | None = Field(default_factory=list, description="Character Usage (JSONB)")


class ContentCreate(ContentBase):
    """Schema for creating a new Content item"""
    pass


class ContentUpdate(BaseModel):
    """Schema for updating an existing Content item (all fields optional)"""
    model_config = ConfigDict(populate_by_name=True)

    company_id: int | None = None
    campaign_id: int | None = Field(default=None, alias="week_id")
    content_type: str | None = None
    publish_date: str | None = None
    publish_time: str | None = None
    publish_day: str | None = None
    status: str | None = None
    h1: list[str] | str | None = None
    caption: str | None = None
    post_images: list[str] | str | None = None
    post_idea: list[str] | str | None = None
    use_character: list[bool] | bool | None = None


class ContentResponse(ContentBase):
    """Schema for Content response returned to user"""
    id: int
    created_at: str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
