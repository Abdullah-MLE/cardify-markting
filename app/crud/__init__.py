from .crud_company import CRUDCompany, company_crud
from .crud_template import CRUDTemplate, template_crud
from .crud_weekly_plan import CRUDWeeklyPlan, weekly_plan_crud
from .crud_content import CRUDContent, content_crud

__all__ = [
    "CRUDCompany",
    "company_crud",
    "CRUDTemplate",
    "template_crud",
    "CRUDWeeklyPlan",
    "weekly_plan_crud",
    "CRUDContent",
    "content_crud",
]
