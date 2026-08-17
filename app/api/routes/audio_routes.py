"""Audio Routes - Transcribe and Audio Processing"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.api.deps import gemini_wrapper
from google.genai import types

import os
import tempfile
from libs.GeminiWrapper.models import InputParams

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribes an audio file to text using Gemini.
    Accepts an audio file via multipart/form-data.
    """
    temp_file_path = None
    try:
        # Create a temporary file to save the uploaded audio
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(await file.read())
            temp_file_path = temp_audio.name

        # Prepare parameters for GeminiWrapper
        input_params = InputParams(
            prompt="Transcribe this audio exactly into text. Output ONLY the text.",
            media=[temp_file_path],
            model="gemini-3-flash-preview"
        )
        
        # Use GeminiWrapper for logs, retries, and error handling
        result = gemini_wrapper.generate_text(input_params=input_params)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Transcription failed"))
            
        transcript = result.get("content", "").strip()
        
        return {
            "success": True,
            "transcript": transcript,
            "file_name": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

