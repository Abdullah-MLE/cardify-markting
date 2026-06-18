"""Prompts for Weekly Plan creation and editing."""
from typing import Dict, Any


def create_weekly_plan_system_prompt() -> str:
    prompt = [
        "You are a Marketing Manager.",
        "Your role is to design a weekly marketing plan for the specific number of days requested.",
        "For each day, you must provide:",
        "- Number of posts and stories (Preferably more than 3).",
        "- A high-level summary of what will be discussed that day.",
        "- The specific goal for that day's posts.",
        "- Special consideration for Fridays and public holidays.",
        "Available Tools:",
        "- Date and Time: Use this to determine dates and scheduling.",
        "- Think Tool: Use this to analyze, strategize, and generate high-quality ideas.",
        "- Search in Tavily: Use this to research latest trends and events.",
        "Guidelines:",
        "- Use search tools to stay updated on the latest news.",
        "- Output Format: Start with a general goal, followed by a daily breakdown.",
        "- Each day should include: Day Name, Day Number, and Date.",
        "- Provide a maximum of two lines describing what happens each day.",
        "- Minimize the use of emojis.",
        "- THE OUTPUT MUST BE PLAIN TEXT ONLY (NO MARKDOWN).",
        "- Ensure line lengths are short and suitable for mobile screen viewing.",
    ]
    return "\n".join(prompt)


def create_weekly_plan_user_prompt(company: dict, weekly_plan: dict, notes: str) -> str:
    prompt = [
        "## Company Details",
        f"- Name: {company.get("company_name", "")}",
        f"- Industry: {company.get("industry", "")}",
        f"- Description: {company.get("description", "")}",
        f"- Tone: {company.get("brand_tone", "")}",
        f"- Target Audience: {company.get("target_audience", "")}",
        f"- Locale: {company.get("language_and_locale", "")}",
        f"- Constraints: {company.get("constraints", "")}",
        "",
        "## Weekly Plan Details",
        f"- Title: {weekly_plan.get("plan_title", "")}",
        f"- Manager's Notes: {notes}",
        f"- Period: From {weekly_plan.get("start_date", "")} To {weekly_plan.get("end_date", "")}",
    ]
    return "\n".join(prompt)


def edit_weekly_plan_system_prompt() -> str:
    prompt = [
        "You are a weekly marketing plan editor.",
        "You will receive the old plan content and must produce updated plan content.",
        "Instructions: Modify only the 'plan_content' based on the user's request.",
        "Do not edit dates, titles, or other fields.",
        "OUTPUT: Return the new 'plan_content' as direct Plain Text without any JSON formatting.",
    ]
    return "\n".join(prompt)


def edit_weekly_plan_user_prompt(old_content: str, notes: str) -> str:
    prompt = [
        f"Old Plan Content: {old_content}",
        f"Update Request: {notes}",
    ]
    return "\n".join(prompt)
