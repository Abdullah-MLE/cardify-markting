from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse


class CRUDContent:
    """CRUD operations for the content table."""

    def __init__(self):
        self.table_name = "content"

    def get(self, db: SupabaseCRUD, content_id: int) -> ContentResponse | None:
        data = db.get_row_by_id(self.table_name, content_id)
        if not data:
            return None
        return ContentResponse(**data)

    def get_by_id(self, db: SupabaseCRUD, content_id: int) -> ContentResponse:
        content = self.get(db, content_id)
        if not content:
            raise ValueError(f"Content with ID {content_id} not found.")
        return content

    def get_by_campaign(self, db: SupabaseCRUD, campaign_id: int) -> list[ContentResponse]:
        response = db.supabase_client.table(self.table_name).select('*').eq('campaign_id', campaign_id).execute()
        return [ContentResponse(**row) for row in response.data] if response.data else []

    def get_by_company(self, db: SupabaseCRUD, company_id: int) -> list[ContentResponse]:
        response = db.supabase_client.table(self.table_name).select('*').eq('company_id', company_id).execute()
        return [ContentResponse(**row) for row in response.data] if response.data else []

    def get_all(self, db: SupabaseCRUD) -> list[ContentResponse]:
        rows = db.get_all_rows(self.table_name)
        return [ContentResponse(**row) for row in rows] if rows else []

    def create(self, db: SupabaseCRUD, obj_in: ContentCreate) -> int:
        if not obj_in.post_images or all(url == "" for url in obj_in.post_images):
            obj_in.status = "pending_images"
        else:
            obj_in.status = "completed"
        data = obj_in.model_dump(exclude_none=True)
        res = db.insert_row(self.table_name, data)
        return res.get("id")

    def update(self, db: SupabaseCRUD, content_id: int, obj_in: ContentUpdate) -> ContentResponse:
        data = obj_in.model_dump(exclude_none=True)
        if "post_images" in data and data["post_images"] is not None:
            if not data["post_images"] or all(url == "" for url in data["post_images"]):
                data["status"] = "pending_images"
            else:
                data["status"] = "completed"
        res = db.update_row(self.table_name, data, content_id)
        if not res:
            raise ValueError(f"Failed to update content {content_id}")
        return ContentResponse(**res)

    def update_images(self, db: SupabaseCRUD, content_id: int, image_urls: list[str]) -> ContentResponse:
        status = "completed" if any(url != "" for url in image_urls) else "pending_images"
        res = db.update_row(self.table_name, {
            "post_images": image_urls,
            "status": status
        }, content_id)
        if not res:
            raise ValueError(f"Failed to update images for content {content_id}")
        return ContentResponse(**res)

    def update_single_image(self, db: SupabaseCRUD, content_id: int, image_url: str, image_index: int = 0) -> ContentResponse:
        current = self.get_by_id(db, content_id)
        post_images = list(current.post_images) if current.post_images and isinstance(current.post_images, list) else []
        while len(post_images) <= image_index:
            post_images.append("")
        post_images[image_index] = image_url
        return self.update_images(db, content_id, post_images)

    def delete(self, db: SupabaseCRUD, content_id: int) -> bool:
        return db.delete_row(self.table_name, content_id)


content_crud = CRUDContent()
