"""Company Routes - Scraping & CRUD"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import scraper_service, base_service
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


# Request Models
class ScrapeRequest(BaseModel):
    url: str


# Actions
@router.post("/extract")
def extract_company_info(req: ScrapeRequest):
    """Scrapes a website and extracts Company info."""
    try:
        markdown = scraper_service.scrape_website(req.url)
        company = scraper_service.extract_company_info(markdown)
        return company.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD
@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int):
    """Gets a company by ID."""
    try:
        return base_service.get_company(company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
def create_company(company: CompanyCreate):
    """Creates a new company."""
    id = base_service.insert_company(company)
    return {"id": id}


@router.put("/{company_id}")
def update_company(company_id: int, company: CompanyUpdate):
    """Updates an existing company."""
    return base_service.update_company(company_id, company)
