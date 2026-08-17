"""Upload Routes - File upload to Supabase Storage"""
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.api.deps import supabase_crud

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file (image, etc.) to Supabase Storage.
    Accepts multipart/form-data, returns the public URL.
    """
    try:
        file_bytes = await file.read()
        content_type = file.content_type or "image/png"
        filename = file.filename or None

        url = supabase_crud.upload_image(
            image_bytes=file_bytes,
            file_name=filename,
            content_type=content_type
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
