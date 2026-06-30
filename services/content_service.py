"""
Content Service
Handles all AI-driven content operations: posts, stories, carousels.
Adapted from old/app/services/content_service.py to use the new DB schema.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.base_service import BaseService
from schemas.db_models import Content
from schemas.ai_models import DayContentGeneration, SinglePostGeneration
from services.prompts.content_prompts import (
    single_post_system_prompt,
    single_post_user_prompt,
    image_gen_system_prompt,
    image_gen_user_prompt,
    image_edit_system_prompt,
    image_edit_user_prompt,
)
from services.prompts.post_prompts import post_image_system_prompt, post_image_user_prompt
from services.prompts.story_prompts import story_image_system_prompt, story_image_user_prompt
from services.prompts.carousel_slide_prompts import (
    carousel_cover_system_prompt,
    carousel_cover_user_prompt,
    carousel_continuation_system_prompt,
    carousel_continuation_user_prompt,
)


class ContentService(BaseService):
    """Unified service for all content operations."""

    # ─── Single Post ──────────────────────────────────────────────────────────

    def create_single_post(self, company_id: int, h1: str, notes: str = "") -> Content:
        """Generates text for a single post and saves it to DB."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()

        user_prompt = single_post_user_prompt(h1, notes, company_dict)
        ai_result: SinglePostGeneration = self.generate_text(
            user_prompt, single_post_system_prompt(), SinglePostGeneration
        )

        content = Content(
            company_id=company_id,
            content_type=ai_result.content_type,
            h1=ai_result.headlines,
            caption=ai_result.caption,
            post_idea=ai_result.post_ideas,
            status="planned",
        )
        content_id = self.insert_content(content)
        content.id = content_id
        return content

    # ─── Image Generation ─────────────────────────────────────────────────────

    def generate_content_media(
        self,
        content_id: int,
        template_id: int | None = None,
        user_prompt: str = None,
    ) -> list[str]:
        """Generate image(s) for a content item based on its type. Returns list of URLs."""
        content = self.get_content(content_id)
        ctype = content.content_type

        if ctype == "post":
            url = self._generate_post_image(content, template_id, user_prompt)
            return [url]
        elif ctype == "story":
            url = self._generate_story_image(content, template_id, user_prompt)
            return [url]
        elif ctype == "carousel":
            return self._generate_carousel_images(content, template_id, user_prompt)
        else:
            raise ValueError(f"Unknown content type: {ctype}")

    def edit_content_media(self, content_id: int, notes: str, slide_index: int = None) -> str:
        """Edit an existing image. Returns new URL."""
        content = self.get_content(content_id)

        if content.content_type == "carousel":
            if slide_index is None:
                raise ValueError("slide_index is required for carousel editing.")
            return self._edit_carousel_slide(content, slide_index, notes)
        else:
            return self._edit_single_image(content, notes)

    # ─── Post Image ───────────────────────────────────────────────────────────

    def _generate_post_image(
        self, content: Content, template_id: int | None, user_instructions: str = None
    ) -> str:
        template_url = self._get_template_url(template_id)
        media = [template_url] if template_url else None

        content_dict = content.model_dump()
        sys_p = post_image_system_prompt()
        usr_p = post_image_user_prompt(content_dict, user_instructions)

        image_bytes = self.generate_image(usr_p, sys_p, media=media, aspect_ratio="1:1")
        return self.upload_image(image_bytes, folder="posts")

    def _edit_single_image(self, content: Content, notes: str) -> str:
        post_images = content.post_images or []
        old_url = post_images[0] if post_images else None
        post_idea = content.post_idea

        idea_str = ""
        if isinstance(post_idea, list) and post_idea:
            idea_str = post_idea[0]
        elif isinstance(post_idea, str):
            idea_str = post_idea

        sys_p = image_edit_system_prompt()
        usr_p = image_edit_user_prompt(idea_str, notes)
        media = [old_url] if old_url else None

        image_bytes = self.generate_image(usr_p, sys_p, media=media)
        return self.upload_image(image_bytes, folder="posts")

    # ─── Story Image ──────────────────────────────────────────────────────────

    def _generate_story_image(
        self, content: Content, template_id: int | None, user_instructions: str = None
    ) -> str:
        template_url = self._get_template_url(template_id)
        media = [template_url] if template_url else None

        content_dict = content.model_dump()
        sys_p = story_image_system_prompt()
        usr_p = story_image_user_prompt(content_dict, user_instructions)

        image_bytes = self.generate_image(usr_p, sys_p, media=media, aspect_ratio="9:16")
        return self.upload_image(image_bytes, folder="stories")

    # ─── Carousel Images ──────────────────────────────────────────────────────

    def _generate_carousel_images(
        self, content: Content, template_id: int | None, user_instructions: str = None
    ) -> list[str]:
        """Generate all carousel slides. First slide uses template; rest match its style."""
        post_idea = content.post_idea or []
        if isinstance(post_idea, str):
            post_idea = [p.strip() for p in post_idea.split("\n---\n") if p.strip()]

        slide_count = len(post_idea)
        if slide_count == 0:
            return []

        template_url = self._get_template_url(template_id)
        content_dict = content.model_dump()

        # Step 1: cover slide
        first_url = self._generate_cover_slide(content_dict, template_url, user_instructions)
        urls = [first_url] + [""] * (slide_count - 1)

        # Step 2: remaining slides in parallel
        if slide_count > 1:
            with ThreadPoolExecutor(max_workers=min(slide_count - 1, 5)) as executor:
                future_to_idx = {
                    executor.submit(self._generate_continuation_slide, content_dict, i, first_url): i
                    for i in range(1, slide_count)
                }
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        urls[idx] = future.result()
                    except Exception as e:
                        print(f"Slide {idx} generation error: {e}")
                        urls[idx] = ""

        return urls

    def _generate_cover_slide(
        self, content_dict: dict, template_url: str | None, user_instructions: str = None
    ) -> str:
        media = [template_url] if template_url else None
        sys_p = carousel_cover_system_prompt()
        usr_p = carousel_cover_user_prompt(content_dict, user_instructions)
        image_bytes = self.generate_image(usr_p, sys_p, media=media)
        return self.upload_image(image_bytes, folder="carousels")

    def _generate_continuation_slide(
        self, content_dict: dict, slide_index: int, first_slide_url: str
    ) -> str:
        sys_p = carousel_continuation_system_prompt()
        usr_p = carousel_continuation_user_prompt(content_dict, slide_index)
        image_bytes = self.generate_image(usr_p, sys_p, media=[first_slide_url])
        return self.upload_image(image_bytes, folder="carousels")

    def _edit_carousel_slide(self, content: Content, slide_index: int, notes: str) -> str:
        post_images = content.post_images or []
        old_url = post_images[slide_index] if slide_index < len(post_images) else None

        post_idea = content.post_idea or []
        if isinstance(post_idea, str):
            post_idea = [p.strip() for p in post_idea.split("\n---\n") if p.strip()]
        idea = post_idea[slide_index] if slide_index < len(post_idea) else ""

        sys_p = image_edit_system_prompt()
        usr_p = image_edit_user_prompt(idea, notes)
        media = [old_url] if old_url else None

        image_bytes = self.generate_image(usr_p, sys_p, media=media)
        return self.upload_image(image_bytes, folder="carousels")

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _get_template_url(self, template_id: int | None) -> str | None:
        if not template_id:
            return None
        try:
            template = self.get_template(template_id)
            return template.template_url
        except Exception:
            return None


# Module-level singleton
_content_service: ContentService | None = None


def get_content_service() -> ContentService:
    global _content_service
    if _content_service is None:
        _content_service = ContentService()
    return _content_service
