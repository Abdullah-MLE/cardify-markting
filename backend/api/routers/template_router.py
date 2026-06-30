"""Template Router."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.api.schemas import AnalyzeTemplateRequest, ExtractTemplateRequest, PromptTemplateRequest, EditTemplateRequest
from services import db_services
from services.template_service import get_template_service
from schemas.ai_models import TemplateAnalysis

router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("/company/{company_id}")
def get_templates(company_id: int):
    """
    Fetches a list of all saved visual templates for a specific company.
    """
    return db_services.get_templates(company_id)

@router.post("/")
def create_template(req: Dict[str, Any]):
    """
    Directly saves a new template's data into the database.
    """
    res = db_services.create_template(req)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to create template")
    return res

@router.put("/{template_id}")
def update_template(template_id: int, req: Dict[str, Any]):
    """
    Updates the information or usage constraints of an existing template in the database.
    """
    res = db_services.update_template(template_id, req)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to update template")
    return res

@router.delete("/{template_id}")
def delete_template(template_id: int):
    """
    Permanently deletes a template from the database.
    """
    if not db_services.delete_template(template_id):
        raise HTTPException(status_code=400, detail="Failed to delete template")
    return {"success": True}

@router.post("/analyze")
def analyze_template(req: AnalyzeTemplateRequest):
    """
    Takes a URL of an existing post image and prompts the AI to analyze its structure, 
    layout, colors, and proportions (extracting its design DNA).
    """
    try:
        svc = get_template_service()
        analysis = svc.analyze_template(req.post_url, req.company_id)
        return analysis.model_dump() if hasattr(analysis, 'model_dump') else analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
def extract_template(req: ExtractTemplateRequest):
    """
    Takes the analysis result from the previous step and prompts the LLM to generate 
    a new, clean, reusable template (blank canvas). The generated image is uploaded to the database.
    """
    try:
        svc = get_template_service()
        analysis_obj = TemplateAnalysis(**req.analysis)
        tpl_bytes = svc.create_template_from_image(analysis_obj, req.company_id, req.post_url, req.instructions)
        tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
        constraints = svc.generate_template_constraints(req.company_id, req.post_url, tpl_url)
        return {"url": tpl_url, "constraints": constraints, "aspect_ratio": analysis_obj.aspect_ratio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.api.schemas import CreateFromImageRequest

@router.post("/create_from_image")
def create_template_from_image(req: CreateFromImageRequest):
    """
    Directly extracts a template image, uploads it, and saves it in the database in a single step.
    """
    try:
        svc = get_template_service()
        
        # Directly generate the template image bytes
        tpl_bytes = svc.create_template_from_image(req.company_id, req.post_url, req.instructions)
        
        # Upload the template image
        tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
        if not tpl_url:
            raise HTTPException(status_code=500, detail="Failed to upload template image")
            
        # Save to DB
        tpl_data = {
            "company_id": req.company_id,
            "template_url": tpl_url,
            "template_constraints": "Use this template for company brand posts. Place headline and details in empty spaces.",
            "template_info": "Extracted from Image",
            "aspect_ratio": "1:1",
            "source_post_url": req.post_url,
            "is_source_same_company": True
        }
        res = db_services.create_template(tpl_data)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompt")
def prompt_template(req: PromptTemplateRequest):
    """
    Generates a brand new template purely from a user's text description (prompt).
    """
    try:
        svc = get_template_service()
        tpl_bytes = svc.create_template_from_prompt(req.company_id, req.prompt, req.aspect_ratio)
        tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
        return {"url": tpl_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{template_id}/edit")
def edit_template(template_id: int, req: EditTemplateRequest):
    """
    Edits an existing template image using AI (Inpainting) based on user instructions or feedback.
    """
    try:
        svc = get_template_service()
        new_bytes = svc.edit_template(template_id, req.notes)
        new_url = db_services.upload_image(new_bytes, folder="templates")
        return {"url": new_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
