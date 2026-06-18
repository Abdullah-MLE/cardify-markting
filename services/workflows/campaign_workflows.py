import datetime
from services.ai_service import get_ai_service
from services import db_services
from services.prompts import campaign_prompts
from schemas.ai_models import DayContentGeneration

def generate_and_save_ai_plan(campaign_id: int, company_id: int, camp: dict, user_brief: str) -> dict:
    """Generates the plain text weekly plan and saves it to the database."""
    ai = get_ai_service()
    company_data = db_services.get_company_data(company_id) or {}
    
    sys_prompt = campaign_prompts.create_weekly_plan_system_prompt()
    user_prompt = campaign_prompts.create_weekly_plan_user_prompt(company_data, camp, user_brief)
    
    result = ai.generate_text(sys_prompt, user_prompt)
    
    if result.get("success"):
        generated_plan_text = result["content"]
        res = db_services.update_campaign(campaign_id, {"ai_plan": generated_plan_text})
        if res is not None:
            return {"success": True, "data": generated_plan_text}
        else:
            return {"success": False, "error": "Failed to update database with generated plan."}
    else:
        return {"success": False, "error": result.get("error")}

def save_edited_campaign_plan(campaign_id: int, edited_plan_str: str) -> dict:
    """Updates the campaign plan text directly in the database."""
    res = db_services.update_campaign(campaign_id, {"ai_plan": edited_plan_str})
    if res is not None:
        return {"success": True, "data": res}
    return {"success": False, "error": "Failed to save edited plan."}

def generate_daily_content_loop(campaign_id: int, company_id: int, camp: dict, ai_plan_raw: str, user_brief: str) -> dict:
    """Loops over the campaign duration to generate detailed JSON content for each day."""
    ai = get_ai_service()
    company_data = db_services.get_company_data(company_id) or {}
    
    try:
        start_dt = datetime.date.fromisoformat(camp.get('start_date', ''))
    except:
        start_dt = datetime.date.today()
        
    try:
        end_dt = datetime.date.fromisoformat(camp.get('end_date', ''))
    except:
        end_dt = start_dt

    num_days = max(1, (end_dt - start_dt).days + 1)
    all_success = True
    errors = []
    
    sys_prompt = campaign_prompts.day_content_system_prompt()
    
    for idx in range(num_days):
        current_dt = start_dt + datetime.timedelta(days=idx)
        day_name = current_dt.strftime("%A")
        day_order = str(idx + 1)
        
        user_prompt = campaign_prompts.day_content_user_prompt(
            company_data, ai_plan_raw, day_name, str(current_dt), day_order, user_brief
        )
        
        res = ai.generate_text(sys_prompt, user_prompt, response_schema=DayContentGeneration)
        
        if res.get("success"):
            day_content_obj = res.get("content", {})
            day_content = day_content_obj.model_dump() if hasattr(day_content_obj, 'model_dump') else day_content_obj.dict() if hasattr(day_content_obj, 'dict') else day_content_obj
            items = day_content.get("content_list", [])
            for item in items:
                db_item = {
                    "company_id": company_id,
                    "campaign_id": campaign_id,
                    "content_type": item.get("type", "post"),
                    "publish_date": str(current_dt),
                    "publish_time": f"{item.get('posting_hour', 12):02d}:00:00",
                    "status": "planned",
                    "h1": item.get("headlines", []),
                    "caption": item.get("caption", ""),
                    "post_images": [], 
                    "publish_day": current_dt.strftime("%A"),
                    "use_character": False,
                    "post_idea": "\n".join(item.get("post_ideas", []))
                }
                db_services.create_content(db_item)
        else:
            errors.append(f"Day {day_order} error: {res.get('error')}")
            all_success = False

    if all_success:
        return {"success": True}
    return {"success": False, "error": "; ".join(errors)}

def create_new_campaign(data: dict) -> dict:
    """Wrapper to create campaign in database."""
    res = db_services.create_campaign(data)
    if res:
        return {"success": True, "data": res}
    return {"success": False, "error": "Database creation failed."}

def update_campaign_details(campaign_id: int, data: dict) -> dict:
    """Wrapper to update campaign in database."""
    res = db_services.update_campaign(campaign_id, data)
    if res is not None:
        return {"success": True, "data": res}
    return {"success": False, "error": "Database update failed."}
