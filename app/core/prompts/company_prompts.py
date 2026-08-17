"""Prompts for Company extraction and editing."""
from app.schemas.company import CompanyBase


def extract_company_system_prompt() -> str:
    prompt = [
        "I'll send you a website markdown.",
        "You should extract the info and return a valid json object.",
        "The json object should have the following fields:",
        "company_name",
        "industry",
        "description",
        "mission_and_goal",
        "brand_tone",
        "target_audience",
        "language_and_locale",
        "constraints",
        "is_character",
        "main_character_name",
        "main_character_constraints",
        "main_character_image_url",
        "visual_constraints",
        "visual_style",
        "brand_color",
        "logo_url",
        "website_url",
        "social_media_username",
        "facebook_url",
        "x_url",
        "instagram_url",
        "linkedin_url",
        "tiktok_url",
        "If you don't know the value for a field, return null.",
        "Return the json object.",
        "Don't add any other text to the response.",
    ]
    return "\n".join(prompt)


def extract_company_user_prompt(markdown: str) -> str:
    prompt = [
        f"Here is the markdown content:",
        f"{markdown}",
    ]
    return "\n".join(prompt)


def edit_company_system_prompt() -> str:
    prompt = [
        "You are a Company Profile Editor.",
        "Update the company details based on the user's notes.",
        "Return the updated JSON object only.",
    ]
    return "\n".join(prompt)


def edit_company_user_prompt(company: CompanyBase, notes: str) -> str:
    prompt = [
        f"Current Details: {company.model_dump_json()}",
        f"User Notes: {notes}",
    ]
    return "\n".join(prompt)
