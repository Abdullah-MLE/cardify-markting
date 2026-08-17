"""Prompts for Single Post generation (text + image in one call)."""
from app.schemas.db_models import Company


def single_post_system_prompt() -> str:
    prompt = [
        "You are an expert social media content creator.",
        "Your task is to generate a SINGLE complete content item from a headline and notes.",
        "",
        "## CONTENT TYPE DETECTION",
        "- If the user asks for a 'carousel' in the notes, set content_type to 'carousel'.",
        "- If the user asks for a 'story' in the notes, set content_type to 'story'.",
        "- Otherwise, default to content_type = 'post'.",
        "",
        "## RULES BY TYPE",
        "### post / story",
        "- 'headlines': List with EXACTLY ONE headline.",
        "- 'post_ideas': List with EXACTLY ONE visual description.",
        "",
        "### carousel",
        "- 'headlines': List of strings, one per slide.",
        "- 'post_ideas': List of strings, one visual description per slide.",
        "- The length of 'headlines' and 'post_ideas' MUST MATCH.",
        "",
        "## GUIDELINES",
        "- Use the company's brand tone and language.",
        "- NO Emojis.",
        "- Visual descriptions (post_ideas) must be in English.",
        "- Headlines and captions follow the company's language/locale.",
        "",
        "## OUTPUT",
        "Return a valid JSON matching SinglePostGeneration schema.",
    ]
    return "\n".join(prompt)


def single_post_user_prompt(h1: str, notes: str, company: Company) -> str:
    prompt = [
        "## HEADLINE",
        f"{h1}",
        "",
        "## USER NOTES",
        f"{notes}" if notes else "No specific notes.",
        "",
        "## COMPANY CONTEXT",
        f"- Name: {company.company_name}",
        f"- Industry: {company.industry}",
        f"- Tone: {company.brand_tone}",
        f"- Audience: {company.target_audience}",
        f"- Locale: {company.language_and_locale}",
        f"- Character: {'Yes - ' + company.main_character_name if company.is_character else 'No'}",
        "",
        "## INSTRUCTION",
        "Generate a complete content item based on the headline and notes above.",
    ]
    return "\n".join(prompt)
