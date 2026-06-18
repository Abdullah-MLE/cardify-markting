"""Prompts for Image generation and editing."""

def image_gen_system_prompt() -> str:
    prompt = [
        "You are an Image Generation Specialist.",
        "Generate prompt for the image model.",
    ]
    return "\n".join(prompt)

def image_gen_user_prompt(headline: str, post_idea: str, template_url: str, use_character: bool) -> str:
    prompt = [
        "Create a social media image.",
        f"Headline: {headline}",
        f"Visual Idea: {post_idea}",
        f"Template Reference: {template_url}",
        f"Use Character: {use_character}",
    ]
    return "\n".join(prompt)

def post_edit_classify_system_prompt() -> str:
    prompt = [
        "You are an assistant that analyzes post edit requests.",
        "Requirement: Decide if the user request is a Text Edit or a Visual Edit (image/design).",
        "If Text Edit: Return JSON with edit_mode = 'text' and text_changes = list of objects {field, value}.",
        "If Visual Edit: Return JSON with edit_mode = 'visual' and visual_changes = list of objects {field, value, editing_prompt}.",
        "OUTPUT: Return strictly JSON matching the schema without any other text.",
    ]
    return "\n".join(prompt)

def post_edit_classify_user_prompt(post_info: str, notes: str) -> str:
    prompt = [
        f"Current Post Info: {post_info}",
        f"User Request: {notes}",
    ]
    return "\n".join(prompt)

def image_edit_system_prompt() -> str:
    prompt = [
        "You are an image editing model.",
        "You will receive an editing prompt and an original image.",
        "Your task: Produce a new image that aligns with the user's request.",
        "OUTPUT: Return the image (binary) only.",
    ]
    return "\n".join(prompt)

def image_edit_user_prompt(post_idea: str, notes: str) -> str:
    prompt = [
        f"Edit this image based on: {notes}",
        f"Context: {post_idea}",
    ]
    return "\n".join(prompt)
