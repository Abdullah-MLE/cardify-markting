"""
Campaign Service
Handles AI-driven campaign plan generation and day content generation.
Works with the 'campaigns' table (replaces old weekly_plans).
"""
import datetime
from services.base_service import BaseService
from schemas.db_models import Campaign
from schemas.ai_models import DayContentGeneration
from services.prompts.campaign_prompts import (
    create_weekly_plan_system_prompt,
    create_weekly_plan_user_prompt,
    day_content_system_prompt,
    day_content_user_prompt,
)


class CampaignService(BaseService):
    """Service for campaign plan generation and daily content creation."""

    # ─── AI Plan Generation ───────────────────────────────────────────────────

    def generate_ai_plan(
        self,
        campaign_id: int,
        company_id: int,
        camp: dict,
        user_brief: str,
    ) -> str:
        """Generate a plain-text AI plan for a campaign. Returns the plan text."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()

        sys_p = create_weekly_plan_system_prompt()
        usr_p = create_weekly_plan_user_prompt(company_dict, camp, user_brief or "")

        plan_text = self.generate_text(usr_p, sys_p)
        return plan_text

    # ─── Daily Content Generation ─────────────────────────────────────────────

    def generate_day_content(
        self,
        company_id: int,
        ai_plan_text: str,
        day_name: str,
        date: str,
        day_order: str,
        user_notes: str = "",
    ) -> DayContentGeneration:
        """Generate structured content items for a single day."""
        company = self.get_company(company_id)
        company_dict = company.model_dump()

        sys_p = day_content_system_prompt()
        usr_p = day_content_user_prompt(
            company_dict, ai_plan_text, day_name, date, day_order, user_notes
        )

        result: DayContentGeneration = self.generate_text(
            usr_p, sys_p, response_schema=DayContentGeneration
        )
        return result

    def generate_campaign_content_loop(
        self,
        campaign_id: int,
        company_id: int,
        camp: dict,
        ai_plan_text: str,
        user_brief: str,
    ) -> dict:
        """
        Loop over each day in the campaign, generate content, and save to DB.
        Returns {"success": True} or {"success": False, "error": ...}.
        """
        from libs.SupabaseClient.supabase_client import SupabaseManager
        client = SupabaseManager.get_client()

        try:
            start_dt = datetime.date.fromisoformat(camp.get("start_date", ""))
        except Exception:
            start_dt = datetime.date.today()
        try:
            end_dt = datetime.date.fromisoformat(camp.get("end_date", ""))
        except Exception:
            end_dt = start_dt

        num_days = max(1, (end_dt - start_dt).days + 1)
        errors = []

        for idx in range(num_days):
            current_dt = start_dt + datetime.timedelta(days=idx)
            day_name = current_dt.strftime("%A")
            day_order = str(idx + 1)

            try:
                day_obj = self.generate_day_content(
                    company_id=company_id,
                    ai_plan_text=ai_plan_text,
                    day_name=day_name,
                    date=str(current_dt),
                    day_order=day_order,
                    user_notes=user_brief,
                )
                day_data = (
                    day_obj.model_dump()
                    if hasattr(day_obj, "model_dump")
                    else day_obj
                )
                items = day_data.get("content_list", [])
                for item in items:
                    db_item = {
                        "company_id": company_id,
                        "campaign_id": campaign_id,
                        "content_type": item.get("type", "post"),
                        "publish_date": str(current_dt),
                        "publish_time": f"{item.get('posting_hour', 12):02d}:00:00",
                        "status": "planned",
                        "h1": item.get("headlines", []),
                        "caption": item.get("caption", ""),
                        "post_images": [],
                        "publish_day": day_name,
                        "use_character": item.get("use_character", False),
                        "post_idea": item.get("post_ideas", []),
                    }
                    client.table("content").insert(db_item).execute()
            except Exception as e:
                errors.append(f"Day {day_order} ({day_name}): {e}")

        if errors:
            return {"success": False, "error": "; ".join(errors)}
        return {"success": True}


# Module-level singleton
_campaign_service: CampaignService | None = None


def get_campaign_service() -> CampaignService:
    global _campaign_service
    if _campaign_service is None:
        _campaign_service = CampaignService()
    return _campaign_service
