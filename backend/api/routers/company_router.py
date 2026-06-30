"""Company Router."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.api.schemas import CompanyCreate, CompanyUpdate, UserCreate, ScrapeRequest, EditProfileRequest
from services import db_services
from services.company_service import get_company_service
from services.scraper_service import get_scraper_service

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/")
def get_companies():
    """
    Fetches a list of all registered companies in the system (used in Admin dashboard).
    """
    return db_services.get_companies()

@router.get("/{company_id}")
def get_company(company_id: int):
    """
    Fetches details of a specific company based on its ID.
    """
    comp = db_services.get_company_data(company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp

@router.post("/")
def create_company(req: CompanyCreate):
    """
    Creates a new company in the database using the provided data (Name, Industry, etc.).
    """
    res = db_services.create_company(req.model_dump())
    if not res:
        raise HTTPException(status_code=400, detail="Failed to create company")
    return res

@router.put("/{company_id}")
def update_company(company_id: int, req: CompanyUpdate):
    """
    Updates an existing company's details (e.g., changing name or updating profile fields).
    """
    res = db_services.update_company(company_id, req.data)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to update company")
    return res

@router.delete("/{company_id}")
def delete_company(company_id: int):
    """
    Completely deletes a company from the database, including all its associated content and campaigns.
    """
    if not db_services.delete_company(company_id):
        raise HTTPException(status_code=400, detail="Failed to delete company")
    return {"success": True}

@router.get("/{company_id}/users")
def get_users(company_id: int):
    """
    Fetches a list of all users linked to this company.
    """
    return db_services.get_company_users(company_id)

@router.post("/users")
def create_user(req: UserCreate):
    """
    Creates a new user account (username/password) and assigns it to the specified company.
    """
    if not db_services.create_user(req.model_dump()):
        raise HTTPException(status_code=400, detail="Failed to create user")
    return {"success": True}

@router.post("/scrape_and_update")
def scrape_and_update(req: ScrapeRequest):
    """
    Visits the given company URL, extracts text, uses the LLM to analyze the 
    content, builds a profile, and immediately updates the company in the database.
    """
    try:
        scraper = get_scraper_service()
        text = scraper.scrape_website(req.url)
        svc = get_company_service()
        profile = svc.extract_company_profile(text)
        
        update_data = {k: v for k, v in profile.model_dump().items() if v is not None}
        if update_data:
            db_services.update_company(req.company_id, update_data)
        return {"success": True, "updated_fields": list(update_data.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit_and_update")
def edit_and_update(req: EditProfileRequest):
    """
    Takes the current company profile and user notes, prompts the LLM to 
    modify the profile, and updates the database immediately.
    """
    try:
        svc = get_company_service()
        updated = svc.edit_company_profile(req.company_data, req.notes)
        
        update_data = {k: v for k, v in updated.model_dump().items() if v is not None}
        if update_data:
            db_services.update_company(req.company_id, update_data)
        return {"success": True, "updated_fields": list(update_data.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
