from services.ai_service import get_ai_service
from services import db_services
from services.prompts import content_prompts
from schemas.ai_models import SinglePostGeneration

def generate_and_attach_image(item: dict, company_id: int, selected_template: dict = None) -> dict:
    """Generates an image for a specific post and attaches it to the database record."""
    ai = get_ai_service()
    
    post_idea = item.get('post_idea', '')
    headline = ", ".join(item.get('h1', [])) if item.get('h1') else ""
    
    template_constraints = selected_template.get('template_constraints', '') if selected_template else ''
    template_url = selected_template.get('template_url') if selected_template else None
    
    sys_prompt = content_prompts.image_gen_system_prompt()
    user_prompt = content_prompts.image_gen_user_prompt(
        prompt=post_idea,
        headline=headline,
        post_idea=post_idea,
        template_constraints=template_constraints
    )
    
    media = [template_url] if template_url else None
    aspect_ratio = selected_template.get('aspect_ratio', '1:1') if selected_template else '1:1'
    
    result = ai.generate_image(sys_prompt, user_prompt, media=media, aspect_ratio=aspect_ratio)
    
    if result.get("success"):
        img_bytes = result["content"]
        img_url = db_services.upload_image(img_bytes)
        if img_url:
            update_data = {"post_images": [img_url]}
            res = db_services.update_content(item['id'], update_data)
            if res:
                return {"success": True, "data": img_url}
            else:
                return {"success": False, "error": "Failed to update database with new image."}
        else:
            return {"success": False, "error": "Failed to upload image to storage."}
    else:
        return {"success": False, "error": result.get("error")}

def edit_content_image(item: dict, notes: str, current_image_bytes: bytes) -> dict:
    """Edits an existing image based on user notes."""
    ai = get_ai_service()
    
    sys_prompt = content_prompts.image_edit_system_prompt()
    user_prompt = content_prompts.image_edit_user_prompt(item.get('post_idea', ''), notes)
    
    # We pass the bytes locally if available, else we'd need to download it
    # Currently, Streamlit image edit uses a local upload or state bytes.
    # Assuming the caller handles getting bytes
    media = [current_image_bytes] if current_image_bytes else None
    
    result = ai.generate_image(sys_prompt, user_prompt, media=media)
    
    if result.get("success"):
        img_bytes = result["content"]
        img_url = db_services.upload_image(img_bytes)
        if img_url:
            update_data = {"post_images": [img_url]}
            db_services.update_content(item['id'], update_data)
            return {"success": True, "data": img_url}
        else:
            return {"success": False, "error": "Failed to upload edited image."}
    else:
        return {"success": False, "error": result.get("error")}

def create_single_post(company_id: int, h1: str, notes: str) -> dict:
    """Creates text content for a single post or carousel."""
    ai = get_ai_service()
    company_data = db_services.get_company_data(company_id) or {}
    
    sys_prompt = content_prompts.single_post_system_prompt()
    user_prompt = content_prompts.single_post_user_prompt(h1, notes, company_data)
    
    res = ai.generate_text(sys_prompt, user_prompt, response_schema=SinglePostGeneration)
    
    if res.get("success"):
        data = res.get("content", {})
        post_obj = data.model_dump() if hasattr(data, 'model_dump') else data.dict() if hasattr(data, 'dict') else data
        
        db_item = {
            "company_id": company_id,
            "content_type": post_obj.get("content_type", "post"),
            "status": "planned",
            "h1": post_obj.get("h1", []),
            "caption": post_obj.get("caption", ""),
            "post_images": [],
            "post_idea": "\n".join(post_obj.get("post_ideas", []))
        }
        item_id = db_services.create_content(db_item)
        if item_id:
            db_item['id'] = item_id
            return {"success": True, "data": db_item}
        else:
            return {"success": False, "error": "Failed to save post to DB."}
    else:
        return {"success": False, "error": res.get("error")}

def generate_standalone_image(prompt: str, company_id: int, selected_template: dict = None) -> dict:
    """Generates an image without attaching it immediately to a content item."""
    ai = get_ai_service()
    
    template_constraints = selected_template.get('template_constraints', '') if selected_template else ''
    template_url = selected_template.get('template_url') if selected_template else None
    
    sys_prompt = content_prompts.image_gen_system_prompt()
    user_prompt = content_prompts.image_gen_user_prompt(
        prompt=prompt,
        headline="",
        post_idea=prompt,
        template_constraints=template_constraints
    )
    
    media = [template_url] if template_url else None
    aspect_ratio = selected_template.get('aspect_ratio', '1:1') if selected_template else '1:1'
    
    result = ai.generate_image(sys_prompt, user_prompt, media=media, aspect_ratio=aspect_ratio)
    
    if result.get("success"):
        return {"success": True, "data": result["content"]}
    return {"success": False, "error": result.get("error")}
