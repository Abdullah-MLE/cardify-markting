from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from backend.api.schemas import ContentCreate, SinglePostRequest, GenerateMediaRequest, EditMediaRequest
from pydantic import BaseModel
from services import db_services
from services.content_service import get_content_service
from services.base_service import BaseService

router = APIRouter(prefix="/content", tags=["content"])

class StandaloneImageRequest(BaseModel):
    company_id: int
    prompt: str
    template_id: Optional[int] = None

@router.get("/company/{company_id}")
def get_scheduled_content(company_id: int):
    """
    Fetches all scheduled and saved content items (posts, stories, carousels) for a specific company.
    """
    return db_services.get_scheduled_content(company_id)

@router.post("/")
def create_content(req: ContentCreate):
    """
    Manually creates a new content item in the database.
    """
    res = db_services.create_content(req.data)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to create content")
    return res

@router.put("/{content_id}")
def update_content(content_id: int, req: ContentCreate):
    """
    Updates an existing content item's details (e.g., modifying the caption or status).
    """
    res = db_services.update_content(content_id, req.data)
    if not res:
        raise HTTPException(status_code=400, detail="Failed to update content")
    return res

@router.delete("/{content_id}")
def delete_content(content_id: int):
    """
    Permanently deletes a content item from the database based on its ID.
    """
    if not db_services.delete_content(content_id):
        raise HTTPException(status_code=400, detail="Failed to delete content")
    return {"success": True}

@router.post("/single_post")
def create_single_post(req: SinglePostRequest):
    """
    Generates a new content post (text) using AI, based on the headline (h1) or idea provided by the user.
    Also automatically links it to a campaign and sets publish dates if provided.
    """
    try:
        svc = get_content_service()
        content = svc.create_single_post(req.company_id, req.h1, req.notes)
        content_dict = content.model_dump() if hasattr(content, 'model_dump') else content
        
        # Immediately update with routing info if provided
        update_data = {}
        if req.campaign_id: update_data["campaign_id"] = req.campaign_id
        if req.publish_date: 
            update_data["publish_date"] = req.publish_date
            # Simple day extraction
            from datetime import date
            try:
                update_data["publish_day"] = date.fromisoformat(req.publish_date).strftime("%A")
            except: pass
        if req.publish_time: 
            pt = req.publish_time
            update_data["publish_time"] = pt + ":00" if len(pt) == 5 else pt
            
        if update_data and "id" in content_dict:
            res = db_services.update_content(content_dict["id"], update_data)
            if res and len(res) > 0:
                content_dict.update(res[0])
                
        return content_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_id}/generate_media")
def generate_media(content_id: int, req: GenerateMediaRequest):
    """
    Generates images (media) for a specific content item based on its visual description. 
    It can optionally apply a selected template during generation.
    """
    try:
        svc = get_content_service()
        urls = svc.generate_content_media(content_id, req.template_id, req.user_instructions)
        return {"urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{content_id}/edit_media")
def edit_media(content_id: int, req: EditMediaRequest):
    """
    Edits an existing image within a content item using AI (Inpainting/Editing) based on user instructions.
    """
    try:
        svc = get_content_service()
        url = svc.edit_content_media(content_id, req.notes, req.slide_index)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_standalone")
def generate_standalone(req: StandaloneImageRequest):
    """
    Generates a standalone image (not linked to any content item) using only a user prompt. 
    Returns the generated image encoded in Base64 format.
    """
    try:
        base = BaseService()
        media = []
        if req.template_id:
            tpl = base.get_template(req.template_id)
            if tpl.template_url:
                media.append(tpl.template_url)
                
        from services.prompts.content_prompts import image_gen_system_prompt, image_gen_user_prompt
        sys_p = image_gen_system_prompt()
        usr_p = image_gen_user_prompt(req.prompt, "", req.prompt, "")
        
        img_bytes = base.generate_image(usr_p, sys_p, media=media)
        # return base64 encoded image
        import base64
        b64_img = base64.b64encode(img_bytes).decode('utf-8')
        return {"image_b64": b64_img}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives an uploaded file from the user, saves it to Supabase storage, 
    and returns the public URL of the uploaded image.
    """
    try:
        contents = await file.read()
        url = db_services.upload_image(contents, folder="uploads")
        if not url:
            raise HTTPException(status_code=500, detail="Failed to upload to Supabase")
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
