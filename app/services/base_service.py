from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams
from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD


class BaseService:
    """Base class for AI operations (Gemini and Storage)."""
    
    def __init__(self, gemini_wrapper: GeminiWrapper, supabase_crud: SupabaseCRUD):
        self.gemini_wrapper = gemini_wrapper
        self.supabase_crud = supabase_crud

    # TEXT GENERATION
    def generate_text(self, prompt: str, system_instruction: str, response_schema=None, media: list = None):
        """Generate text. If response_schema is provided, returns structured JSON. Otherwise plain text."""
        input_params = InputParams(prompt=prompt, system_instruction=system_instruction, media=media)
        
        if response_schema:
            text_params = TextParams(response_schema=response_schema, response_mime_type='application/json')
            result = self.gemini_wrapper.generate_text(input_params=input_params, text_params=text_params)
        else:
            result = self.gemini_wrapper.generate_text(input_params=input_params)
        
        if not result.get("success"):
            raise Exception(f"AI generation failed: {result.get('error')}")
        return result.get("content")

    # IMAGE GENERATION
    def generate_image(self, prompt: str, system_instruction: str, media: list = None, aspect_ratio: str = "3:4") -> bytes:
        input_params = InputParams(prompt=prompt, system_instruction=system_instruction, media=media)
        image_params = ImageParams(output_image_aspect_ratio=aspect_ratio)
        result = self.gemini_wrapper.generate_image(input_params=input_params, image_params=image_params)
        if not result.get("success"):
            raise Exception(f"Image generation failed: {result.get('error')}")
        return result.get("content")

    # STORAGE HELPER
    def upload_image(self, image_bytes: bytes, filename: str) -> str:
        return self.supabase_crud.upload_image(image_bytes, filename)
