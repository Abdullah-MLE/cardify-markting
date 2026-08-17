"""Prompts for Day Content generation and editing."""
from app.schemas.company import CompanyBase
from app.schemas.weekly_plan import WeeklyPlanBase


def day_content_system_prompt() -> str:
    prompt = [
        "You are an expert social media strategist.",
        "Your task is to generate a daily content plan as a LIST of items.",
        "",
        "## UNIFIED CONTENT STRUCTURE",
        "Every content item (Post, Story, Carousel) shares the same structure but uses the lists differently.",
        "Structure: type, headlines (list), caption (string), post_ideas (list), posting_hour, use_character.",
        "",
        "## RULES BY TYPE",
        "### 1. Posts and Stories ('post', 'story')",
        "- 'headlines': List containing EXACTLY ONE headline.",
        "- 'post_ideas': List containing EXACTLY ONE visual description.",
        "- 'caption': Single caption.",
        "",
        "### 2. Carousels ('carousel')",
        "- 'headlines': List of strings. Each string is the text for one slide.",
        "- 'post_ideas': List of strings. Each string is the visual description for one slide.",
        "- 'caption': Single caption for the whole carousel.",
        "**Important**: The length of 'headlines' and 'post_ideas' MUST MATCH.",
        "",
        "## CONTENT GUIDELINES",
        "- Language: ARABIC (headlines/captions), English (internal ideas).",
        "- Tone: Use company brand tone.",
        "- NO Emojis.",
        "",
        "## OUTPUT FORMAT",
        "Return a valid JSON object matching DayContentGeneration schema.",
        "It contains content_list: [item1, item2, ...].",
    ]
    return "\n".join(prompt)


def day_content_user_prompt(company: CompanyBase, weekly_plan: WeeklyPlanBase, day_name: str, date: str, day_order: str, notes: str) -> str:
    prompt = [
        "## CONTEXT",
        f"Company: {company.company_name} ({company.industry})",
        f"Target Audience: {company.target_audience}",
        f"Tone: {company.brand_tone}",
        f"Munaasik Character: {'Yes' if company.is_character else 'No'}",
        "",
        "## WEEKLY STRATEGY",
        f"Title: {weekly_plan.plan_title}",
        f"Focus: {weekly_plan.ai_plan}",
        "",
        "## TODAY'S TASK",
        f"Day: {day_name} ({date}) - Day Order: {day_order}",
        f"Manager Notes: {notes}",
        "",
        "## INSTRUCTION",
        "Generate the optimal mix of content (posts, stories, carousels) to achieve the day's goal.",
        "Ensure variety and alignment with the weekly focus.",
    ]
    return "\n".join(prompt)


def edit_day_content_system_prompt() -> str:
    prompt = [
        "You are a social media editor.",
        "Update the content based on the user's request.",
        "Return the updated JSON object.",
    ]
    return "\n".join(prompt)


def edit_day_content_user_prompt(day_content_json: str, notes: str) -> str:
    prompt = [
        f"Current Content: {day_content_json}",
        f"User Update Request: {notes}",
    ]
    return "\n".join(prompt)
