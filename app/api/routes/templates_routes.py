"""Template Routes - Actions & CRUD"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import template_service, template_crud, supabase_crud
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter(prefix="/templates", tags=["Templates"])


# Request Models
class CreateTemplateRequest(BaseModel):
    company_id: int
    post_url: str | None = None
    prompt: str | None = None

class EditRequest(BaseModel):
    template_id: int
    notes: str


# Actions
@router.post("/create")
def create_template(req: CreateTemplateRequest):
    """Creates a template from a post (Analysis -> Generation -> Constraints) OR a prompt."""
    try:
        if req.post_url:
            analysis = template_service.analyze_template(req.post_url, req.company_id)
            url = template_service.create_template_from_image(analysis, req.company_id, req.post_url, req.prompt)
            constraints = template_service.generate_template_constraints(req.company_id, req.post_url, url)
            return {
                "template_url": url, 
                "constraints": constraints
            }
        elif req.prompt:
            url = template_service.create_template_from_prompt(req.company_id, req.prompt)
            constraints = template_service.generate_template_constraints(req.company_id, url, url)
            return {
                "template_url": url,
                "constraints": constraints
            }
        else:
             raise HTTPException(status_code=400, detail="Either post_url or prompt must be provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit")
def edit_template(req: EditRequest):
    """Edits an existing template."""
    try:
        url = template_service.edit_template(req.template_id, req.notes)
        return {"template_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD
@router.get("", response_model=list[TemplateResponse])
def list_templates(company_id: int = None):
    """Lists templates, optionally filtered by company_id."""
    return template_crud.get_all(supabase_crud, company_id=company_id)


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int):
    """Gets a template by ID."""
    try:
        return template_crud.get_by_id(supabase_crud, template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
def insert_template(template: TemplateCreate):
    """Creates a new template record."""
    id = template_crud.create(supabase_crud, template)
    return {"id": id}


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateUpdate):
    """Updates an existing template."""
    try:
        return template_crud.update(supabase_crud, template_id, template)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
