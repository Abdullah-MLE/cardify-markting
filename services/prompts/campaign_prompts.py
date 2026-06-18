"""Prompts for Campaign Workflows."""

def create_weekly_plan_system_prompt() -> str:
    prompt = [
        "You are a Marketing Manager.",
        "Your role is to design a weekly marketing plan for the specific number of days requested.",
        "For each day, you must provide:",
        "- Number of posts and stories (Preferably more than 3).",
        "- A high-level summary of what will be discussed that day.",
        "- The specific goal for that day's posts.",
        "- Special consideration for Fridays and public holidays.",
        "Guidelines:",
        "- Start with a general goal, followed by a daily breakdown.",
        "- Each day should include: Day Name, Day Number, and Date.",
        "- Provide a maximum of two lines describing what happens each day.",
        "- Minimize the use of emojis.",
        "- THE OUTPUT MUST BE PLAIN TEXT ONLY (NO MARKDOWN)."
    ]
    return "\n".join(prompt)

def create_weekly_plan_user_prompt(company: dict, campaign: dict, notes: str) -> str:
    prompt = [
        "## Company Details",
        f"- Name: {company.get('company_name', '')}",
        f"- Industry: {company.get('industry', '')}",
        f"- Description: {company.get('description', '')}",
        f"- Tone: {company.get('brand_tone', '')}",
        f"- Target Audience: {company.get('target_audience', '')}",
        f"- Locale: {company.get('language_and_locale', '')}",
        f"- Constraints: {company.get('constraints', '')}",
        "",
        "## Weekly Plan Details",
        f"- Title: {campaign.get('plan_title', '')}",
        f"- Manager's Notes: {notes}",
        f"- Period: From {campaign.get('start_date', '')} To {campaign.get('end_date', '')}",
    ]
    return "\n".join(prompt)

def day_content_system_prompt() -> str:
    prompt = [
        "You are an expert social media strategist.",
        "Your task is to generate a daily content plan as a LIST of items.",
        "",
        "## UNIFIED CONTENT STRUCTURE",
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
        "It contains content_list: [item1, item2, ...]."
    ]
    return "\n".join(prompt)

def day_content_user_prompt(company: dict, weekly_plan: str, day_name: str, date: str, day_order: str, notes: str) -> str:
    prompt = [
        "## CONTEXT",
        f"Company: {company.get('company_name', '')} ({company.get('industry', '')})",
        f"Target Audience: {company.get('target_audience', '')}",
        f"Tone: {company.get('brand_tone', '')}",
        f"Munaasik Character: {'Yes' if company.get('is_character', '') else 'No'}",
        "",
        "## WEEKLY STRATEGY / AI PLAN",
        f"{weekly_plan}",
        "",
        "## TODAY'S TASK",
        f"Day: {day_name} ({date}) - Day Order: {day_order}",
        f"Manager Notes: {notes}",
        "",
        "## INSTRUCTION",
        "Generate the optimal mix of content (posts, stories, carousels) to achieve the day's goal.",
        "Ensure variety and alignment with the weekly focus."
    ]
    return "\n".join(prompt)
