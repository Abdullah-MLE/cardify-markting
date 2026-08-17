"""Prompts for Carousel first slide (cover) and continuation slides."""
from app.schemas.content import ContentBase


def carousel_cover_system_prompt() -> str:
    prompt = [
        "You are a carousel cover designer.",
        "Create an engaging first slide that sets the visual style for the entire carousel.",
        "This slide will be used as reference for all following slides.",
    ]
    return "\n".join(prompt)


def carousel_cover_user_prompt(content: ContentBase, user_instructions: str = None) -> str:
    headline = content.h1[0] if content.h1 else ""
    post_idea = content.post_idea[0] if content.post_idea else ""
    prompt = [
        "Create a Carousel Cover Slide (First Slide).",
        f"Headline: {headline}",
        f"Visual Idea: {post_idea}",
        "This is the primary slide - establish the visual style.",
    ]
    if user_instructions:
        prompt.append(f"Additional Instructions: {user_instructions}")
    return "\n".join(prompt)


def carousel_continuation_system_prompt() -> str:
    prompt = [
        "You are a carousel slide designer.",
        "Create a slide that matches the style of the provided reference image (first slide).",
        "Keep the same background, colors, and overall aesthetic.",
        "Only change the content, text, and foreground elements.",
    ]
    return "\n".join(prompt)


def carousel_continuation_user_prompt(content: ContentBase, slide_index: int) -> str:
    headline = content.h1[slide_index] if content.h1 and slide_index < len(content.h1) else ""
    post_idea = content.post_idea[slide_index] if content.post_idea and slide_index < len(content.post_idea) else ""
    prompt = [
        f"Create Carousel Slide {slide_index + 1}.",
        f"Headline: {headline}",
        f"Visual Idea: {post_idea}",
        "IMPORTANT: Match the style of the reference image (first slide).",
        "Keep the same background and visual style.",
        "Only update the text content and main elements.",
    ]
    return "\n".join(prompt)
