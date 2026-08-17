from libs.SupabaseCRUD.SupabaseCRUD import SupabaseCRUD
from app.schemas.weekly_plan import WeeklyPlanCreate, WeeklyPlanUpdate, WeeklyPlanResponse


class CRUDWeeklyPlan:
    """CRUD operations for the campaigns (weekly_plans) table."""

    def __init__(self):
        self.table_name = "campaigns"

    def get_by_id(self, db: SupabaseCRUD, plan_id: int) -> WeeklyPlanResponse:
        data = db.get_row_by_id(self.table_name, plan_id)
        if not data:
            raise ValueError(f"Weekly plan with ID {plan_id} not found.")
        return WeeklyPlanResponse(**data)

    def get_all(self, db: SupabaseCRUD, company_id: int = None) -> list[WeeklyPlanResponse]:
        """Get all campaigns, optionally filtered by company_id."""
        if company_id:
            response = db.supabase_client.table(self.table_name).select('*').eq('company_id', company_id).execute()
            return [WeeklyPlanResponse(**row) for row in response.data] if response.data else []
        rows = db.get_all_rows(self.table_name)
        return [WeeklyPlanResponse(**row) for row in rows] if rows else []

    def create(self, db: SupabaseCRUD, obj_in: WeeklyPlanCreate) -> int:
        if obj_in.ai_plan and (obj_in.status == "draft" or not obj_in.status):
            obj_in.status = "planned"
        data = obj_in.model_dump(exclude_none=True)
        res = db.insert_row(self.table_name, data)
        return res.get("id")

    def update(self, db: SupabaseCRUD, plan_id: int, obj_in: WeeklyPlanUpdate) -> WeeklyPlanResponse:
        if obj_in.ai_plan and (obj_in.status == "draft" or not obj_in.status):
            obj_in.status = "planned"
        data = obj_in.model_dump(exclude_none=True)
        res = db.update_row(self.table_name, data, plan_id)
        if not res:
            raise ValueError(f"Failed to update weekly plan {plan_id}")
        return WeeklyPlanResponse(**res)

    def delete(self, db: SupabaseCRUD, plan_id: int) -> bool:
        return db.delete_row(self.table_name, plan_id)


weekly_plan_crud = CRUDWeeklyPlan()
