"""Campaign Router."""
from fastapi import APIRouter, HTTPException
from backend.api.schemas import CampaignCreate, CampaignUpdate, GeneratePlanRequest, GenerateContentRequest
from services import db_services
from services.campaign_service import get_campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.get("/company/{company_id}")
def get_campaigns(company_id: int):
    """
    Fetches all campaigns and weekly plans associated with a specific company.
    """
    return db_services.get_campaigns(company_id)

@router.post("/")
def create_campaign(req: CampaignCreate):
    """
    Creates a new campaign/weekly plan (as an empty time frame and title) for a company.
    """
    res = db_services.create_campaign(req.model_dump())
    if not res:
        raise HTTPException(status_code=400, detail="Failed to create campaign")
    return res

@router.put("/{campaign_id}")
def update_campaign(campaign_id: int, req: CampaignUpdate):
    """
    Updates campaign details (e.g., start/end dates, or the generated AI plan text).
    """
    res = db_services.update_campaign(campaign_id, req.data)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to update campaign")
    return res

@router.post("/generate_plan")
def generate_ai_plan(req: GeneratePlanRequest):
    """
    Prompts the AI to generate a weekly content plan based on the company's profile,
    the campaign date range, and any additional manager notes provided by the user.
    """
    try:
        svc = get_campaign_service()
        plan_text = svc.generate_ai_plan(req.campaign_id, req.company_id, req.camp_data, req.user_brief)
        return {"ai_plan": plan_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_content")
def generate_campaign_content(req: GenerateContentRequest):
    """
    Takes the generated weekly plan text and prompts the LLM to extract detailed 
    individual posts for each day. Then, it saves each post separately into the content table.
    """
    try:
        svc = get_campaign_service()
        res = svc.generate_campaign_content_loop(
            req.campaign_id, req.company_id, req.camp_data, req.ai_plan_text, req.user_brief
        )
        if not res.get("success"):
            raise HTTPException(status_code=500, detail=res.get("error"))
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
