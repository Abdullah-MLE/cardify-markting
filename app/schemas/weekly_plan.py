from pydantic import BaseModel, Field, ConfigDict


class WeeklyPlanBase(BaseModel):
    """Common fields for WeeklyPlan (Campaign)"""
    model_config = ConfigDict(populate_by_name=True)

    company_id: int
    plan_title: str
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = Field(default="draft")
    ai_plan: str | None = Field(default=None, alias="plan_content")


class WeeklyPlanCreate(WeeklyPlanBase):
    """Schema for creating a new WeeklyPlan"""
    pass


class WeeklyPlanUpdate(BaseModel):
    """Schema for updating an existing WeeklyPlan (all fields optional)"""
    model_config = ConfigDict(populate_by_name=True)

    company_id: int | None = None
    plan_title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    ai_plan: str | None = Field(default=None, alias="plan_content")


class WeeklyPlanResponse(WeeklyPlanBase):
    """Schema for WeeklyPlan response returned to user"""
    id: int
    created_at: str | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
