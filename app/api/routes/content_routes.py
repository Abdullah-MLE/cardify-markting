"""Content Routes - Actions & CRUD"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import content_service, content_crud, weekly_plan_crud, supabase_crud
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse
from app.schemas.weekly_plan import WeeklyPlanUpdate

router = APIRouter(prefix="/content", tags=["Content"])


# Request Models
class CreateWeekContentRequest(BaseModel):
    weekly_plan_id: int

class CreateDayContentRequest(BaseModel):
    weekly_plan_id: int
    day_order: int
    day_name: str
    date: str
    notes: str = "no notes"

class CreateContentImageRequest(BaseModel):
    content_id: int
    template_id: int
    user_prompt: str | None = None

class EditContentImageRequest(BaseModel):
    content_id: int
    notes: str
    slide_index: int | None = None

class CreateSinglePostRequest(BaseModel):
    company_id: int
    template_id: int
    h1: str
    notes: str = ""


# Actions
@router.post("/create-week")
def create_week_content(req: CreateWeekContentRequest):
    """Generates content for the full week."""
    try:
        results = content_service.generate_week_content(req.weekly_plan_id)
        weekly_plan_crud.update(supabase_crud, req.weekly_plan_id, WeeklyPlanUpdate(status="content_ready"))
        return {"days": [d.model_dump() for d in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-day")
def create_day_content(req: CreateDayContentRequest):
    """Generates content items for a specific day."""
    try:
        day_content = content_service.generate_day_content(
            req.weekly_plan_id, req.day_order, req.day_name, req.date, req.notes
        )
        weekly_plan_crud.update(supabase_crud, req.weekly_plan_id, WeeklyPlanUpdate(status="content_ready"))
        return day_content.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-image")
def create_content_image(req: CreateContentImageRequest):
    """Generates image(s) for a content item based on its type."""
    try:
        result = content_service.generate_content_media(
            req.content_id, req.template_id, req.user_prompt
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit-image")
def edit_content_image(req: EditContentImageRequest):
    """Edits an existing image."""
    try:
        result = content_service.edit_content_media(
            req.content_id, req.notes, req.slide_index
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-single-post")
def create_single_post(req: CreateSinglePostRequest):
    """Creates a complete post (text + images) from h1 + notes."""
    try:
        content = content_service.create_single_post(
            req.company_id, req.template_id, req.h1, req.notes
        )
        return {
            "content_id": content.id,
            "content_type": content.content_type,
            "h1": content.h1,
            "caption": content.caption,
            "post_images": content.post_images,
            "post_idea": content.post_idea,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD
@router.get("", response_model=list[ContentResponse])
def list_content(company_id: int = None, campaign_id: int = None):
    """Lists content, optionally filtered by company_id and/or campaign_id."""
    return content_crud.get_all(supabase_crud, company_id=company_id, campaign_id=campaign_id)


@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int):
    """Gets content by ID."""
    try:
        return content_crud.get_by_id(supabase_crud, content_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
def insert_content(content: ContentCreate):
    """Creates a new content record."""
    id = content_crud.create(supabase_crud, content)
    return {"id": id}


@router.put("/{content_id}", response_model=ContentResponse)
def update_content(content_id: int, content: ContentUpdate):
    """Updates content record."""
    try:
        return content_crud.update(supabase_crud, content_id, content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
