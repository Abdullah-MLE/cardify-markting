from datetime import date, timedelta
from app.services.base_service import BaseService
from app.crud import company_crud, weekly_plan_crud
from app.schemas.weekly_plan import WeeklyPlanBase
from app.core.prompts import (
    create_weekly_plan_system_prompt, 
    create_weekly_plan_user_prompt,
    edit_weekly_plan_system_prompt,
    edit_weekly_plan_user_prompt
)


class WeeklyPlanService(BaseService):

    def create_weekly_plan(self, company_id: int, title: str = None, start_date: str = None, end_date: str = None, user_notes: str = "just make a weekly plan") -> WeeklyPlanBase:
        """Generates a weekly marketing plan content using LLM."""       
        today = date.today()
        start = start_date or today.isoformat()
        end = end_date or (date.fromisoformat(start) + timedelta(days=7)).isoformat()
        plan_title = title or f"Weekly Plan {start}"

        company = company_crud.get_by_id(self.supabase_crud, company_id)
        
        # Create temporary WeeklyPlanBase object for the prompt
        weekly_plan = WeeklyPlanBase(
            company_id=company_id,
            plan_title=plan_title,
            start_date=start,
            end_date=end
        )
        
        system_prompt = create_weekly_plan_system_prompt()
        user_prompt = create_weekly_plan_user_prompt(company, weekly_plan, user_notes)
        
        result = self.generate_text(user_prompt, system_prompt)
        if not result:
            raise Exception("Weekly plan creation failed")
            
        weekly_plan.ai_plan = result
        return weekly_plan

    def edit_weekly_plan(self, weekly_plan_id: int, notes: str) -> str:
        """Edits the text content of an existing weekly plan."""
        weekly_plan = weekly_plan_crud.get_by_id(self.supabase_crud, weekly_plan_id)
        
        system_prompt = edit_weekly_plan_system_prompt()
        user_prompt = edit_weekly_plan_user_prompt(weekly_plan.ai_plan or "", notes)
        
        result = self.generate_text(user_prompt, system_prompt)
        if not result:
            raise Exception("Weekly plan edit failed")
        return result
