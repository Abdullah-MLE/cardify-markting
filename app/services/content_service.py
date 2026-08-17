from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.base_service import BaseService
from app.schemas.db_models import Content
from app.schemas.ai_models import DayContentGeneration, ContentItem, SinglePostGeneration
from app.core.prompts import day_content_system_prompt, day_content_user_prompt
from app.core.prompts import single_post_system_prompt, single_post_user_prompt
from app.core.prompts import post_image_system_prompt, post_image_user_prompt
from app.core.prompts import story_image_system_prompt, story_image_user_prompt
from app.core.prompts import image_edit_system_prompt, image_edit_user_prompt
from app.core.prompts.carousel_slide_prompts import (
    carousel_cover_system_prompt,
    carousel_cover_user_prompt,
    carousel_continuation_system_prompt,
    carousel_continuation_user_prompt
)
import time


class ContentService(BaseService):
    """Unified service for all content operations: posts, stories, carousels."""

    # UNIFIED ENTRY POINTS
    def generate_week_content(self, weekly_plan_id: int) -> list[DayContentGeneration]:
        """Generates content for the full week."""
        from datetime import date, timedelta
        weekly_plan = self.get_weekly_plan(weekly_plan_id)
        start = date.fromisoformat(weekly_plan.start_date) if weekly_plan.start_date else date.today()
        
        days_of_week = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        
        results = [None] * 7
        with ThreadPoolExecutor(max_workers=7) as executor:
            future_to_index = {
                executor.submit(
                    self.generate_day_content, 
                    weekly_plan_id, 
                    i+1, 
                    day_name, 
                    (start + timedelta(days=i)).isoformat()
                ): i 
                for i, day_name in enumerate(days_of_week)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    raise e
        
        return results

    def create_single_post(self, company_id: int, template_id: int, h1: str, notes: str = "") -> Content:
        """Creates a complete post (text + images) from a headline and notes."""
        company = self.get_company(company_id)

        # Step 1: Generate text via AI
        user_prompt = single_post_user_prompt(h1, notes, company)
        ai_result = self.generate_text(user_prompt, single_post_system_prompt(), SinglePostGeneration)

        # Step 2: Build Content and insert to DB
        content = Content(
            company_id=company_id,
            content_type=ai_result.content_type,
            h1=ai_result.headlines,
            caption=ai_result.caption,
            post_idea=ai_result.post_ideas,
            use_character=ai_result.use_character,
        )
        content_id = self.insert_content(content)

        # Step 3: Generate images
        image_urls = self.generate_content_media(content_id, template_id)

        # Step 4: Save images to DB
        if isinstance(image_urls, str):
            image_urls = [image_urls]
        self.update_content_images(content_id, image_urls)

        # Step 5: Return full Content from DB
        return self.get_content(content_id)

    def generate_content_media(self, content_id: int, template_id: int, user_prompt: str = None) -> str | list[str]:
        """Unified method to generate media based on content type."""
        content = self.get_content(content_id)
        if content.content_type == "post":
            return self.generate_post_image(content_id, template_id, user_prompt)
        elif content.content_type == "story":
            return self.generate_story_image(content_id, template_id, user_prompt)
        elif content.content_type == "carousel":
            return self.generate_carousel_images(content_id, template_id, user_prompt)
        else:
            raise ValueError(f"Unknown content type: {content.content_type}")

    def edit_content_media(self, content_id: int, notes: str, slide_index: int = None) -> str:
        """Unified method to edit media."""
        content = self.get_content(content_id)
        
        if content.content_type == "carousel":
            if slide_index is None:
                raise ValueError("slide_index is required for editing carousel")
            return self.edit_carousel_slide_image(content_id, slide_index, notes)
        elif content.content_type == "post":
            return self.edit_post_image(content_id, notes)
        elif content.content_type == "story":
            return self.edit_story_image(content_id, notes)
        else:
             raise ValueError(f"Unknown content type: {content.content_type}")

    # TEXT GENERATION
    def generate_day_content(self, weekly_plan_id: int, day_order: int, day_name: str, date: str, notes: str = "no notes") -> DayContentGeneration:
        """Generates a LIST of content (posts, stories, carousels) for the day."""
        weekly_plan = self.get_weekly_plan(weekly_plan_id)
        company = self.get_company(weekly_plan.company_id)
        
        user_prompt = day_content_user_prompt(company, weekly_plan, day_name, date, str(day_order), notes)
        return self.generate_text(user_prompt, day_content_system_prompt(), DayContentGeneration)

    # DATABASE CRUD
    def insert_content(self, content: Content) -> int:
        """Inserts a Content row into the database."""
        data = content.model_dump(exclude_none=True, exclude={"id", "created_at"})
        res = self.supabase_crud.insert_row("content", data)
        return res.get("id")

    def update_content_image(self, content_id: int, image_url: str, image_index: int = 0) -> None:
        """Updates a specific image URL in content.post_images."""
        content = self.get_content(content_id)
        if not content.post_images:
            content.post_images = []
        while len(content.post_images) <= image_index:
            content.post_images.append("")
        content.post_images[image_index] = image_url
        
        status = "completed" if any(url != "" for url in content.post_images) else "pending_images"
        self.supabase_crud.update_row("content", {
            "post_images": content.post_images,
            "status": status
        }, content_id)

    def update_content_images(self, content_id: int, image_urls: list[str]) -> None:
        """Updates all image URLs in content.post_images."""
        status = "completed" if any(url != "" for url in image_urls) else "pending_images"
        self.supabase_crud.update_row("content", {
            "post_images": image_urls,
            "status": status
        }, content_id)

    # POST IMAGE GENERATION
    def generate_post_image(self, content_id: int, template_id: int, user_instructions: str = None) -> str:
        """Generates a single image for Post. Returns URL only."""
        content = self.get_content(content_id)
        template = self.get_template(template_id)
        
        system_prompt = post_image_system_prompt()
        user_prompt = post_image_user_prompt(content, user_instructions)
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[template.template_url])
        return self.upload_image(image_bytes, f"post-{content_id}-{int(time.time())}.png")

    def edit_post_image(self, content_id: int, notes: str) -> str:
        """Edits an existing post image based on notes. Returns new URL."""
        content = self.get_content(content_id)
        old_image_url = content.post_images[0] if content.post_images else ""
        
        system_prompt = image_edit_system_prompt()
        user_prompt = image_edit_user_prompt(content.post_idea[0] if content.post_idea else "", notes)
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[old_image_url])
        return self.upload_image(image_bytes, f"post-{content_id}-edited-{int(time.time())}.png")

    # STORY IMAGE GENERATION
    def generate_story_image(self, content_id: int, template_id: int, user_instructions: str = None) -> str:
        """Generates a single image for Story. Returns URL only."""
        content = self.get_content(content_id)
        template = self.get_template(template_id)
        
        system_prompt = story_image_system_prompt()
        user_prompt = story_image_user_prompt(content, user_instructions)
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[template.template_url], aspect_ratio="9:16")
        return self.upload_image(image_bytes, f"story-{content_id}-{int(time.time())}.png")

    def edit_story_image(self, content_id: int, notes: str) -> str:
        """Edits an existing story image based on notes. Returns new URL."""
        content = self.get_content(content_id)
        old_image_url = content.post_images[0] if content.post_images else ""
        
        system_prompt = image_edit_system_prompt()
        user_prompt = image_edit_user_prompt(content.post_idea[0] if content.post_idea else "", notes)
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[old_image_url], aspect_ratio="9:16")
        return self.upload_image(image_bytes, f"story-{content_id}-edited-{int(time.time())}.png")

    # CAROUSEL IMAGE GENERATION
    def generate_carousel_images(self, content_id: int, template_id: int, user_instructions: str = None) -> list[str]:
        """
        Generates images for ALL slides.
        - First slide: uses template
        - Other slides: generated in parallel, matching first slide style
        """
        content = self.get_content(content_id)
        template = self.get_template(template_id)
        slide_count = len(content.post_idea) if content.post_idea else 0
        
        if slide_count == 0:
            return []
        
        urls = [""] * slide_count
        
        # Step 1: Generate FIRST slide with template
        first_slide_url = self._generate_cover_slide(content, template.template_url, user_instructions)
        urls[0] = first_slide_url
        
        # Step 2: Generate remaining slides in PARALLEL
        if slide_count > 1:
            with ThreadPoolExecutor(max_workers=min(slide_count - 1, 5)) as executor:
                future_to_index = {
                    executor.submit(self._generate_continuation_slide, content, i, first_slide_url): i
                    for i in range(1, slide_count)
                }
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        urls[index] = future.result()
                    except Exception as e:
                        print(f"Error generating slide {index}: {e}")
                        urls[index] = ""
        
        return urls

    def _generate_cover_slide(self, content: Content, template_url: str, user_instructions: str = None) -> str:
        """Generate first slide using template."""
        system_prompt = carousel_cover_system_prompt()
        user_prompt = carousel_cover_user_prompt(content, user_instructions)
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[template_url])
        return self.upload_image(image_bytes, f"carousel-{content.id}-cover-{int(time.time())}.png")

    def _generate_continuation_slide(self, content: Content, slide_index: int, first_slide_url: str) -> str:
        """Generate continuation slide matching first slide style."""
        system_prompt = carousel_continuation_system_prompt()
        user_prompt = carousel_continuation_user_prompt(content, slide_index)
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[first_slide_url])
        return self.upload_image(image_bytes, f"carousel-{content.id}-slide-{slide_index}-{int(time.time())}.png")

    def generate_single_slide_image(self, content_id: int, slide_index: int, template_id: int) -> str:
        """Generates a single slide image."""
        content = self.get_content(content_id)
        template = self.get_template(template_id)
        
        if slide_index == 0:
            return self._generate_cover_slide(content, template.template_url)
        else:
            first_slide_url = content.post_images[0] if content.post_images else ""
            if not first_slide_url:
                return self._generate_cover_slide(content, template.template_url)
            return self._generate_continuation_slide(content, slide_index, first_slide_url)

    def edit_carousel_slide_image(self, content_id: int, slide_index: int, notes: str) -> str:
        """Edits a single slide image based on notes."""
        content = self.get_content(content_id)
        old_image_url = content.post_images[slide_index] if content.post_images and slide_index < len(content.post_images) else ""
        post_idea = content.post_idea[slide_index] if content.post_idea and slide_index < len(content.post_idea) else ""
        
        system_prompt = image_edit_system_prompt()
        user_prompt = image_edit_user_prompt(post_idea, notes)
        
        image_bytes = self.generate_image(user_prompt, system_prompt, media=[old_image_url])
        return self.upload_image(image_bytes, f"carousel-{content_id}-slide-{slide_index}-edited-{int(time.time())}.png")
