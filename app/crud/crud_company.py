from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse


class CRUDCompany:
    """CRUD operations for the companies table."""

    def __init__(self):
        self.table_name = "companies"

    def get(self, db: SupabaseCRUD, company_id: int) -> CompanyResponse | None:
        data = db.get_row_by_id(self.table_name, company_id)
        if not data:
            return None
        return CompanyResponse(**data)

    def get_by_id(self, db: SupabaseCRUD, company_id: int) -> CompanyResponse:
        company = self.get(db, company_id)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found.")
        return company

    def get_all(self, db: SupabaseCRUD) -> list[CompanyResponse]:
        rows = db.get_all_rows(self.table_name)
        return [CompanyResponse(**row) for row in rows] if rows else []

    def create(self, db: SupabaseCRUD, obj_in: CompanyCreate) -> int:
        data = obj_in.model_dump(exclude_none=True)
        res = db.insert_row(self.table_name, data)
        return res.get("id")

    def update(self, db: SupabaseCRUD, company_id: int, obj_in: CompanyUpdate) -> CompanyResponse:
        data = obj_in.model_dump(exclude_none=True)
        res = db.update_row(self.table_name, data, company_id)
        if not res:
            raise ValueError(f"Failed to update company {company_id}")
        return CompanyResponse(**res)

    def delete(self, db: SupabaseCRUD, company_id: int) -> bool:
        return db.delete_row(self.table_name, company_id)


company_crud = CRUDCompany()
