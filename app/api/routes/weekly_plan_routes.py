"""Weekly Plan Routes - Actions & CRUD"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import weekly_plan_service, supabase_crud, base_service
from app.schemas.db_models import WeeklyPlan

router = APIRouter(prefix="/weekly-plans", tags=["Weekly Plans"])


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


# Actions
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
    """Edits the content of an existing weekly plan."""
    try:
        content = weekly_plan_service.edit_weekly_plan(req.weekly_plan_id, req.notes)
        return {"ai_plan": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD
@router.get("/{plan_id}")
def get_weekly_plan(plan_id: int):
    """Gets a weekly plan by ID."""
    try:
        return base_service.get_weekly_plan(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
def insert_weekly_plan(plan: WeeklyPlan):
    """Creates a new weekly plan record."""
    id = base_service.insert_weekly_plan(plan)
    return {"id": id}


@router.put("/{plan_id}")
def update_weekly_plan(plan_id: int, plan: WeeklyPlan):
    """Updates a weekly plan."""
    return base_service.update_weekly_plan(plan_id, plan)
