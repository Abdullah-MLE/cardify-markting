from .company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
from .template import (
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
)
from .weekly_plan import (
    WeeklyPlanBase,
    WeeklyPlanCreate,
    WeeklyPlanUpdate,
    WeeklyPlanResponse,
)
from .content import (
    ContentBase,
    ContentCreate,
    ContentUpdate,
    ContentResponse,
)
from .ai_models import (
    DayContentGeneration,
    ContentItem,
    SinglePostGeneration,
    TempletAnalysis,
    EditResponse,
)

# Aliases for backward compatibility
Company = CompanyResponse
Template = TemplateResponse
WeeklyPlan = WeeklyPlanResponse
Campaign = WeeklyPlanResponse
Content = ContentResponse

__all__ = [
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "Company",
    # Template
    "TemplateBase",
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    "Template",
    # WeeklyPlan / Campaign
    "WeeklyPlanBase",
    "WeeklyPlanCreate",
    "WeeklyPlanUpdate",
    "WeeklyPlanResponse",
    "WeeklyPlan",
    "Campaign",
    # Content
    "ContentBase",
    "ContentCreate",
    "ContentUpdate",
    "ContentResponse",
    "Content",
    # AI Models
    "DayContentGeneration",
    "ContentItem",
    "SinglePostGeneration",
    "TempletAnalysis",
    "EditResponse",
]
