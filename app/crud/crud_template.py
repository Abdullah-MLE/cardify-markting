from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse


class CRUDTemplate:
    """CRUD operations for the templates table."""

    def __init__(self):
        self.table_name = "templates"

    def get_by_id(self, db: SupabaseCRUD, template_id: int) -> TemplateResponse:
        data = db.get_row_by_id(self.table_name, template_id)
        if not data:
            raise ValueError(f"Template with ID {template_id} not found.")
        return TemplateResponse(**data)

    def get_all(self, db: SupabaseCRUD, company_id: int = None) -> list[TemplateResponse]:
        """Get all templates, optionally filtered by company_id."""
        if company_id:
            response = db.supabase_client.table(self.table_name).select('*').eq('company_id', company_id).execute()
            return [TemplateResponse(**row) for row in response.data] if response.data else []
        rows = db.get_all_rows(self.table_name)
        return [TemplateResponse(**row) for row in rows] if rows else []

    def create(self, db: SupabaseCRUD, obj_in: TemplateCreate) -> int:
        data = obj_in.model_dump(exclude_none=True)
        res = db.insert_row(self.table_name, data)
        return res.get("id")

    def update(self, db: SupabaseCRUD, template_id: int, obj_in: TemplateUpdate) -> TemplateResponse:
        data = obj_in.model_dump(exclude_none=True)
        res = db.update_row(self.table_name, data, template_id)
        if not res:
            raise ValueError(f"Failed to update template {template_id}")
        return TemplateResponse(**res)

    def delete(self, db: SupabaseCRUD, template_id: int) -> bool:
        return db.delete_row(self.table_name, template_id)


template_crud = CRUDTemplate()
