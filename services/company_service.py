"""
Company Service
Handles AI-driven company profile extraction and management.
Replaces old company_workflows.py.
"""
import json
from services.base_service import BaseService
from schemas.ai_models import CompanyExtraction
from services.prompts.company_prompts import (
    extract_company_system_prompt,
    extract_company_user_prompt,
    edit_company_system_prompt,
    edit_company_user_prompt,
)


class CompanyService(BaseService):
    """Service for company profile extraction and AI-assisted editing."""

    def extract_company_profile(self, source_text: str) -> CompanyExtraction:
        """Extract a structured company profile from raw text or website markdown."""
        sys_p = extract_company_system_prompt()
        usr_p = extract_company_user_prompt(source_text)
        return self.generate_text(usr_p, sys_p, CompanyExtraction)

    def edit_company_profile(self, company_data: dict, notes: str) -> CompanyExtraction:
        """Edit an existing company profile based on AI notes."""
        sys_p = edit_company_system_prompt()
        try:
            company_json = json.dumps(company_data, ensure_ascii=False)
        except Exception:
            company_json = str(company_data)
        usr_p = edit_company_user_prompt(company_json, notes)
        return self.generate_text(usr_p, sys_p, CompanyExtraction)


# Module-level singleton
_company_service: CompanyService | None = None


def get_company_service() -> CompanyService:
    global _company_service
    if _company_service is None:
        _company_service = CompanyService()
    return _company_service
