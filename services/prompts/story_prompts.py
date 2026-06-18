"""Simple prompts for Story image generation."""
from typing import Dict, Any


def story_image_system_prompt() -> str:
    prompt = [
        "You are a social media story designer.",
        "Create an engaging story image.",
    ]
    return "\n".join(prompt)


def story_image_user_prompt(content: dict, user_instructions: str = None) -> str:
    headline = content.get("h1", [])[0] if content.get("h1", []) else ""
    post_idea = content.get("post_idea", "")[0] if content.get("post_idea", "") else ""
    prompt = [
        "Create an Instagram Story image.",
        f"Headline: {headline}",
        f"Visual Idea: {post_idea}",
    ]
    if user_instructions:
        prompt.append(f"Additional Instructions: {user_instructions}")
    return "\n".join(prompt)
