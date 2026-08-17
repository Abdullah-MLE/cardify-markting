from pydantic import BaseModel, Field

# AI Response Models (for generation)


class ContentItem(BaseModel):
    """Unified AI model for all content types."""
    type: str = Field(..., description="'post', 'story', 'carousel'")
    headlines: list[str] = Field(..., description="List of headlines. 1 for post/story, multiple for carousel.")
    post_ideas: list[str] = Field(..., description="List of visual descriptions. 1 for post/story, multiple for carousel.")
    use_character: list[bool] = Field(..., description="Use character in the content.")
    posting_hour: int = Field(..., description="Hour of day (0-23)")
    caption: str = Field(..., description="Single caption for the content.")


class SinglePostGeneration(BaseModel):
    """AI response for generating a single complete post from h1 + notes."""
    content_type: str = Field(default="post", description="'post', 'story', or 'carousel'")
    headlines: list[str] = Field(..., description="List of headlines. 1 for post/story, multiple for carousel.")
    post_ideas: list[str] = Field(..., description="List of visual descriptions. 1 for post/story, multiple for carousel.")
    caption: str = Field(..., description="Caption for the content.")
    use_character: list[bool] = Field(default_factory=list, description="Use character per slide/post.")


class DayContentGeneration(BaseModel):
    """
    Container for all content generated for a specific day.
    Can include multiple posts, stories, and carousels.
    """
    content_list: list[ContentItem] = Field(default_factory=list)


# Helper Models (not DB)

class TempletAnalysis(BaseModel):
    is_same_company: bool
    aspect_ratio: str
    change: list[str]
    keep: list[str]
    remove: list[str]



class EditResponse(BaseModel):
    edit_mode: str
    text_changes: list[dict] = Field(default_factory=list)
    visual_changes: list[dict] = Field(default_factory=list)
