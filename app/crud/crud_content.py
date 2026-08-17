from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse


class CRUDContent:
    """CRUD operations for the content table."""

    def __init__(self):
        self.table_name = "content"

    def get_by_id(self, db: SupabaseCRUD, content_id: int) -> ContentResponse:
        data = db.get_row_by_id(self.table_name, content_id)
        if not data:
            raise ValueError(f"Content with ID {content_id} not found.")
        return ContentResponse(**data)

    def get_all(self, db: SupabaseCRUD, company_id: int = None, campaign_id: int = None) -> list[ContentResponse]:
        """Get all content, optionally filtered by company_id and/or campaign_id."""
        query = db.supabase_client.table(self.table_name).select('*')
        if company_id:
            query = query.eq('company_id', company_id)
        if campaign_id:
            query = query.eq('campaign_id', campaign_id)
        response = query.execute()
        return [ContentResponse(**row) for row in response.data] if response.data else []

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
        # Auto-manage status when post_images changes
        if "post_images" in data and data["post_images"] is not None:
            if not data["post_images"] or all(url == "" for url in data["post_images"]):
                data["status"] = "pending_images"
            else:
                data["status"] = "completed"
        res = db.update_row(self.table_name, data, content_id)
        if not res:
            raise ValueError(f"Failed to update content {content_id}")
        return ContentResponse(**res)

    def delete(self, db: SupabaseCRUD, content_id: int) -> bool:
        return db.delete_row(self.table_name, content_id)


content_crud = CRUDContent()
