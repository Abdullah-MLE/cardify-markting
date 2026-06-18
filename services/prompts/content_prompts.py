"""Prompts for Content Workflows (Text and Image Generation)."""

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
        "Return a valid JSON matching SinglePostGeneration schema."
    ]
    return "\n".join(prompt)

def single_post_user_prompt(h1: str, notes: str, company: dict) -> str:
    prompt = [
        "## HEADLINE",
        f"{h1}",
        "",
        "## USER NOTES",
        f"{notes}" if notes else "No specific notes.",
        "",
        "## COMPANY CONTEXT",
        f"- Name: {company.get('company_name', '')}",
        f"- Industry: {company.get('industry', '')}",
        f"- Tone: {company.get('brand_tone', '')}",
        f"- Audience: {company.get('target_audience', '')}",
        f"- Locale: {company.get('language_and_locale', '')}",
        f"- Character: {'Yes' if company.get('is_character', '') else 'No'}",
        "",
        "## INSTRUCTION",
        "Generate a complete content item based on the headline and notes above."
    ]
    return "\n".join(prompt)

def image_gen_system_prompt() -> str:
    prompt = [
        "You are an Image Generation Specialist.",
        "Generate a high-quality image based on the prompt.",
    ]
    return "\n".join(prompt)

def image_gen_user_prompt(prompt: str, headline: str, post_idea: str, template_constraints: str) -> str:
    text = [
        "Create a social media image.",
        f"Prompt Idea: {prompt}",
        f"Headline (For Context): {headline}",
        f"Visual Context: {post_idea}",
        f"Template Constraints (Must Follow): {template_constraints}",
    ]
    return "\n".join(text)

def image_edit_system_prompt() -> str:
    prompt = [
        "You are an image editing model.",
        "You will receive an editing prompt and an original image.",
        "Your task: Produce a new image that aligns with the user's request."
    ]
    return "\n".join(prompt)

def image_edit_user_prompt(post_idea: str, notes: str) -> str:
    prompt = [
        f"Edit this image based on the user request: {notes}",
        f"Original Context: {post_idea}",
    ]
    return "\n".join(prompt)
