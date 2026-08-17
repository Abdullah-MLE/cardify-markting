"""Simple prompts for Post image generation."""
from app.schemas.content import ContentBase


def post_image_system_prompt() -> str:
    prompt = [
        "You are a social media image designer.",
        "Create a visually appealing post image.",
    ]
    return "\n".join(prompt)


def post_image_user_prompt(content: ContentBase, user_instructions: str = None) -> str:
    headline = content.h1[0] if content.h1 else ""
    post_idea = content.post_idea[0] if content.post_idea else ""
    prompt = [
        "Create an Instagram post image.",
        f"Headline: {headline}",
        f"Visual Idea: {post_idea}",
    ]
    if user_instructions:
        prompt.append(f"Additional Instructions: {user_instructions}")
    return "\n".join(prompt)
