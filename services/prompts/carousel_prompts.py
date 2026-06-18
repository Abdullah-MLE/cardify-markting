"""Prompts for Carousel text generation (not image)."""

def carousel_gen_system_prompt() -> str:
    prompt = [
        "You are a Carousel Generator.",
        "Create a sequence of images/slides.",
    ]
    return "\n".join(prompt)

def carousel_gen_user_prompt(headline: str, post_idea: str) -> str:
    prompt = [
        f"Create a carousel for: {headline}",
        f"Visual Idea: {post_idea}",
    ]
    return "\n".join(prompt)

def carousel_edit_system_prompt() -> str:
    prompt = [
        "Edit the carousel slides.",
    ]
    return "\n".join(prompt)

def carousel_edit_user_prompt(notes: str) -> str:
    prompt = [
        f"Edit the carousel based on: {notes}",
    ]
    return "\n".join(prompt)
