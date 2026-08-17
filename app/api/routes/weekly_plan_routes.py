"""Campaigns (Weekly Plans) Routes - Actions & CRUD"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import weekly_plan_service, weekly_plan_crud, supabase_crud
from app.schemas.weekly_plan import WeeklyPlanCreate, WeeklyPlanUpdate, WeeklyPlanResponse

router = APIRouter(tags=["Campaigns"])


# Request Models
class CreateRequest(BaseModel):
    company_id: int
    start_date: str | None = None
    end_date: str | None = None
    title: str | None = None
    notes: str | None = None


class EditRequest(BaseModel):
    weekly_plan_id: int
    notes: str


# Actions (AI)
@router.post("/create")
def create_weekly_plan(req: CreateRequest):
    """Generates a weekly plan using AI."""
    try:
        result = weekly_plan_service.create_weekly_plan(
            company_id=req.company_id,
            title=req.title,
            start_date=req.start_date,
            end_date=req.end_date,
            user_notes=req.notes or "just make a weekly plan"
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit")
def edit_weekly_plan(req: EditRequest):
    """Edits the content of an existing weekly plan using AI."""
    try:
        content = weekly_plan_service.edit_weekly_plan(req.weekly_plan_id, req.notes)
        return {"ai_plan": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD
@router.get("", response_model=list[WeeklyPlanResponse])
def list_campaigns(company_id: int = None):
    """Lists campaigns, optionally filtered by company_id."""
    return weekly_plan_crud.get_all(supabase_crud, company_id=company_id)


@router.get("/{plan_id}", response_model=WeeklyPlanResponse)
def get_campaign(plan_id: int):
    """Gets a campaign by ID."""
    try:
        return weekly_plan_crud.get_by_id(supabase_crud, plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
def insert_campaign(plan: WeeklyPlanCreate):
    """Creates a new campaign record."""
    id = weekly_plan_crud.create(supabase_crud, plan)
    return {"id": id}


@router.put("/{plan_id}", response_model=WeeklyPlanResponse)
def update_campaign(plan_id: int, plan: WeeklyPlanUpdate):
    """Updates a campaign."""
    try:
        return weekly_plan_crud.update(supabase_crud, plan_id, plan)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
