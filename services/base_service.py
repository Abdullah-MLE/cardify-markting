"""
Base Service
Shared helpers for all AI services.
Uses the existing GeminiWrapper and SupabaseClient.
"""
from libs.GeminiWrapper.GeminiWrapper import GeminiWrapper
from libs.GeminiWrapper.models import InputParams, TextParams, ImageParams
from libs.SupabaseClient.supabase_client import SupabaseManager
from schemas.db_models import Company, Campaign, Template, Content


def _get_client():
    """Return the shared Supabase client."""
    return SupabaseManager.get_client()


class BaseService:
    """Base class with shared helpers for all services."""

    def __init__(self) -> None:
        self.gemini = GeminiWrapper()

    # ─── Entity Getters ───────────────────────────────────────────────────────

    def get_company(self, company_id: int) -> Company:
        client = _get_client()
        res = client.table("companies").select("*").eq("id", company_id).execute()
        if not res.data:
            raise ValueError(f"Company {company_id} not found.")
        return Company(**res.data[0])

    def get_campaign(self, campaign_id: int) -> Campaign:
        client = _get_client()
        res = client.table("campaigns").select("*").eq("id", campaign_id).execute()
        if not res.data:
            raise ValueError(f"Campaign {campaign_id} not found.")
        return Campaign(**res.data[0])

    def get_template(self, template_id: int) -> Template:
        client = _get_client()
        res = client.table("templates").select("*").eq("id", template_id).execute()
        if not res.data:
            raise ValueError(f"Template {template_id} not found.")
        return Template(**res.data[0])

    def get_content(self, content_id: int) -> Content:
        client = _get_client()
        res = client.table("content").select("*").eq("id", content_id).execute()
        if not res.data:
            raise ValueError(f"Content {content_id} not found.")
        return Content(**res.data[0])

    # ─── Entity Inserters ─────────────────────────────────────────────────────

    def insert_content(self, content: Content) -> int:
        client = _get_client()
        data = content.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = client.table("content").insert(data).execute()
        return res.data[0]["id"] if res.data else None

    def insert_template(self, template: Template) -> int:
        client = _get_client()
        data = template.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = client.table("templates").insert(data).execute()
        return res.data[0]["id"] if res.data else None

    # ─── Entity Updaters ──────────────────────────────────────────────────────

    def update_content_images(self, content_id: int, image_urls: list[str]) -> None:
        client = _get_client()
        client.table("content").update({"post_images": image_urls}).eq("id", content_id).execute()

    # ─── AI: Text Generation ──────────────────────────────────────────────────

    def generate_text(
        self,
        prompt: str,
        system_instruction: str,
        response_schema=None,
        media: list = None,
    ):
        """Generate text. Returns parsed object if schema given, else plain text."""
        input_params = InputParams(
            prompt=prompt,
            system_instruction=system_instruction,
            media=media,
        )
        text_params = None
        if response_schema:
            text_params = TextParams(
                response_schema=response_schema,
                response_mime_type="application/json",
            )
        result = self.gemini.generate_text(input_params=input_params, text_params=text_params)
        if not result.get("success"):
            raise Exception(f"AI text generation failed: {result.get('error')}")
        return result.get("content")

    # ─── AI: Image Generation ─────────────────────────────────────────────────

    def generate_image(
        self,
        prompt: str,
        system_instruction: str,
        media: list = None,
        aspect_ratio: str = "1:1",
    ) -> bytes:
        """Generate an image and return raw bytes."""
        input_params = InputParams(
            prompt=prompt,
            system_instruction=system_instruction,
            media=media,
        )
        image_params = ImageParams(output_image_aspect_ratio=aspect_ratio)
        result = self.gemini.generate_image(input_params=input_params, image_params=image_params)
        if not result.get("success"):
            raise Exception(f"AI image generation failed: {result.get('error')}")
        return result.get("content")

    # ─── Storage ──────────────────────────────────────────────────────────────

    def upload_image(self, image_bytes: bytes, folder: str = "generated") -> str:
        """Upload image bytes to Supabase storage and return public URL."""
        from services.db_services import upload_image
        return upload_image(image_bytes, folder=folder)
