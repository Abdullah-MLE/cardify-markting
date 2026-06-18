import json
from services.ai_service import get_ai_service
from services import db_services
from services.prompts import company_prompts
from schemas.ai_models import CompanyExtraction

def analyze_and_extract_company_profile(source_text: str) -> dict:
    """Analyzes raw text (like website markdown) and extracts a structured company profile."""
    ai = get_ai_service()
    
    sys_prompt = company_prompts.extract_company_system_prompt()
    user_prompt = company_prompts.extract_company_user_prompt(source_text)
    
    result = ai.generate_text(sys_prompt, user_prompt, response_schema=CompanyExtraction)
    
    if result.get("success"):
        data = result.get("content", {})
        profile = data.model_dump() if hasattr(data, 'model_dump') else data.dict() if hasattr(data, 'dict') else data
        return {"success": True, "data": profile}
    return {"success": False, "error": result.get("error")}

def edit_company_profile(company_data: dict, notes: str) -> dict:
    """Edits a company profile based on user notes using AI."""
    ai = get_ai_service()
    
    sys_prompt = company_prompts.edit_company_system_prompt()
    try:
        company_json = json.dumps(company_data, ensure_ascii=False)
    except Exception:
        company_json = str(company_data)
        
    user_prompt = company_prompts.edit_company_user_prompt(company_json, notes)
    
    result = ai.generate_text(sys_prompt, user_prompt, response_schema=CompanyExtraction)
    
    if result.get("success"):
        data = result.get("content", {})
        profile = data.model_dump() if hasattr(data, 'model_dump') else data.dict() if hasattr(data, 'dict') else data
        return {"success": True, "data": profile}
    return {"success": False, "error": result.get("error")}

def save_company_profile(company_data: dict) -> dict:
    """Saves a company profile to the database."""
    res = db_services.create_company(company_data)
    if res:
        return {"success": True, "data": res}
    return {"success": False, "error": "Failed to create company in database."}

def update_company_profile(company_id: int, company_data: dict) -> dict:
    """Updates an existing company profile in the database."""
    res = db_services.update_company(company_id, company_data)
    if res is not None:
        return {"success": True, "data": res}
    return {"success": False, "error": "Failed to update company in database."}
