from pydantic import BaseModel, Field
from typing import List, Optional


class ContentItem(BaseModel):
    """A single content item in a day's content plan."""

    type: str = Field(..., description="'post', 'story', 'carousel'")
    headlines: List[str] = Field(
        ...,
        description="List of headlines. 1 for post/story, multiple for carousel.",
    )
    post_ideas: List[str] = Field(
        ...,
        description="Visual descriptions. 1 for post/story, multiple for carousel.",
    )
    posting_hour: int = Field(..., description="Hour of day (0-23)")
    caption: str = Field(..., description="Caption for the content.")


class SinglePostGeneration(BaseModel):
    """Schema for generating a single post / story / carousel."""

    content_type: str = Field(
        default="post", description="'post', 'story', or 'carousel'"
    )
    headlines: List[str] = Field(..., description="List of headlines.")
    post_ideas: List[str] = Field(
        ..., description="List of visual descriptions."
    )
    caption: str = Field(..., description="Caption for the content.")


class DayContentGeneration(BaseModel):
    """Schema for a full day of content items."""

    content_list: List[ContentItem] = Field(default_factory=list)


class TemplateAnalysis(BaseModel):
    """Result of analysing a design template against a brand."""

    is_same_company: bool
    aspect_ratio: str
    change: List[str]
    keep: List[str]
    remove: List[str]


class CompanyExtraction(BaseModel):
    """Extracted company profile from user-supplied info."""

    company_name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    mission_and_goal: Optional[str] = None
    brand_tone: Optional[str] = None
    target_audience: Optional[str] = None
    language_and_locale: Optional[str] = None
    website_url: Optional[str] = None


class DayPlan(BaseModel):
    """A single day within a weekly content plan."""

    day_name: str
    theme: str
    content_types: List[str] = Field(default_factory=list)


class WeeklyPlanGeneration(BaseModel):
    """Schema for a full weekly content plan."""

    plan_title: str
    days: List[DayPlan] = Field(default_factory=list)
