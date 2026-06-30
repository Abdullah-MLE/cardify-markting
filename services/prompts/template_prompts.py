"""Prompts for Template analysis, generation, and editing."""
from typing import Dict, Any
from schemas.ai_models import TemplateAnalysis


def template_analysis_system_prompt() -> str:
    prompt = [
        "You are an AI assistant analyzing a social media post to extract a template.",
        "The user will provide a post design image and their company logo/details.",
        "Your task is to analyze the image and output a JSON containing:",
        "1. is_same_company: True if the design matches the user's company branding, False otherwise.",
        "2. aspect_ratio: The aspect ratio of the post design (Choose from: 1:1, 3:4, 4:3, 9:16, 16:9).",
        "3. keep: List of visual elements that must remain in the blank template (e.g., logo position, footer layout, background shapes).",
        "4. change: List of elements that should change per post (e.g., product image, main headline text, phone numbers).",
        "5. remove: List of elements that should be deleted completely (e.g., unrelated contact details, specific campaign logos).",
        "Ensure your analysis isolates creative temporary content from permanent brand layout structures.",
    ]
    return "\n".join(prompt)


def template_analysis_user_prompt(company: dict) -> str:
    prompt = [
        "## Company Profile",
        f"- Name: {company.get('company_name', '')}",
        f"- Industry: {company.get('industry', '')}",
        f"- Description: {company.get('description', '')}",
        f"- Mission and Goal: {company.get('mission_and_goal', '')}",
        f"- Brand Tone: {company.get('brand_tone', '')}",
        f"- Target Audience: {company.get('target_audience', '')}",
        f"- Locale: {company.get('language_and_locale', '')}",
        f"- Brand Colors: {company.get('brand_color', '')}",
        f"- Visual Style: {company.get('visual_style', '')}",
        f"- Visual Constraints: {company.get('visual_constraints', '')}",
        f"- Main Character: {company.get('main_character_name', '')} (Is Character: {company.get('is_character', '')})",
        f"- Character Constraints: {company.get('main_character_constraints', '')}",
        f"- Character Image: {company.get('main_character_image_url', '')}",
        f"- Website: {company.get('website_url', '')}",
        f"- Social Media Username: {company.get('social_media_username', '')}",
        f"- Facebook: {company.get('facebook_url', '')}",
        f"- X (Twitter): {company.get('x_url', '')}",
        f"- Instagram: {company.get('instagram_url', '')}",
        f"- LinkedIn: {company.get('linkedin_url', '')}",
        f"- TikTok: {company.get('tiktok_url', '')}",
        f"- General Constraints: {company.get('constraints', '')}",
    ]
    return "\n".join(prompt)


def template_creation_from_prompt_system_prompt() -> str:
    prompt = [
        "You are a professional graphic designer.",
        "Your job is to generate a blank social media template image based on the user's text description and company profile.",
        "Make sure the template is beautiful, aligned with the company branding, and completely empty of any temporary post text, people, or product images.",
        "Only generate the background design, layout shapes, and layout placeholders (header, footer, logo area).",
    ]
    return "\n".join(prompt)


def template_creation_from_prompt_user_prompt(company: dict, user_request: str) -> str:
    prompt = [
        "## User Request",
        f"{user_request}",
        "",
        "## Company Profile",
        f"- Name: {company.get('company_name', '')}",
        f"- Industry: {company.get('industry', '')}",
        f"- Description: {company.get('description', '')}",
        f"- Mission: {company.get('mission_and_goal', '')}",
        f"- Tone: {company.get('brand_tone', '')}",
        f"- Audience: {company.get('target_audience', '')}",
        f"- Colors: {company.get('brand_color', '')}",
        f"- Style: {company.get('visual_style', '')}",
        f"- Constraints: {company.get('constraints', '')} {company.get('visual_constraints', '')}",
        f"- Character: {company.get('main_character_name', '') if company.get('is_character', '') else 'None'}",
        f"- Socials: {company.get('social_media_username', '')}",
    ]
    return "\n".join(prompt)


def template_generation_system_prompt() -> str:
    prompt = [
        "You are an AI image generator specializing in blank social media templates.",
        "You will receive a source post image, the company logo, and instructions on what elements to keep, change, or remove.",
        "Generate a blank reusable template image.",
        "Keep the logo exactly in the specified position.",
        "Remove all post text, products, and temporary foreground elements.",
        "Keep only the core design background and branding shapes.",
    ]
    return "\n".join(prompt)


def template_generation_user_prompt(analysis: TemplateAnalysis) -> str:
    prompt = [
        "Create the template image based on this analysis:",
        f"- Change: {analysis.change}",
        f"- Keep Elements: {', '.join(analysis.keep)}",
        f"- Remove Elements: {', '.join(analysis.remove)}",
        "Reset the background to a solid, neutral color or the brand's standard texture.",
        "Keep the company logo EXACTLY in the position described.",
    ]
    return "\n".join(prompt)


def template_constraint_system_prompt() -> str:
    prompt = [
        "You are a Brand Consistency Enforcer.",
        "Your task is to compare the Original Post and the Generated Template to create strict usage rules (constraints).",
        "These constraints will guide future AI models on how to correctly place content on this template without breaking the design.",
        "Output: Plain text list of strict instructions.",
    ]
    return "\n".join(prompt)


def template_constraint_user_prompt(company: dict) -> str:
    prompt = [
        f"Company: {company.get('company_name', '')}",
        "I have provided the Original Post and the New Blank Template.",
        "Compare them and write strict instructions on how to use this new template.",
        "Identify:",
        "1. Where the logo is fixed (and warn not to cover it).",
        "2. Where the contact info is fixed (and warn not to cover it).",
        "3. Where the main headline should go.",
        "4. Where the main image/visual should go.",
        "5. Any specific warnings like 'Do not place a white box behind the logo' or 'Do not change the footer'.",
        "Make the instructions imperative and strict.",
    ]
    return "\n".join(prompt)


def template_usage_system_prompt() -> str:
    prompt = [
        "Explain how to use this template.",
    ]
    return "\n".join(prompt)


def template_usage_user_prompt() -> str:
    prompt = [
        "Explain how to use this template.",
    ]
    return "\n".join(prompt)


def template_edit_system_prompt() -> str:
    prompt = [
        "You are an assistant for editing design templates.",
        "Your task is to modify the template based on the user's request while maintaining the core brand constraints.",
        "Instructions: If the edit is textual (like constraints or description), return a JSON defining the new text fields.",
        "If it's visual (like dimensions or shape), return a JSON containing 'editing_prompt' to generate a new image as well as the text fields to update.",
        "OUTPUT: Return JSON only without extra text.",
    ]
    return "\n".join(prompt)


def template_edit_user_prompt(notes: str) -> str:
    prompt = [
        f"User Request: {notes}",
    ]
    return "\n".join(prompt)
