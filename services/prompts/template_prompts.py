"""Prompts for Template analysis, generation, and editing."""
from typing import Dict, Any
from schemas.ai_models import TemplateAnalysis


def template_analysis_system_prompt() -> str:
    prompt = [
        "بص اليوزر هيبعت لك post عايز يعمله templet",
        "وهيبعت صوره الشعار بتاع شركته ومعلومات الشركه كامله",
        "مطلوب منك تقول أولا هل نفس الشركه ولا لا",
        "عشان ممكن يبعت نفس الشركه",
        "ثانيا تقول ال aspect_ratio بتاعت ال post",
        "خلي بالك ممكن يبعت اسكرين شوت مثلا انت لازم تحدد فين ال post بالظبط وتقول ال aspect_ratio بتاعته",
        "اختار من هنا  1:1, 3:4, 4:3, 9:16, 16:9",
        "ثالثا بناء على معلومات الشركه لازم تحدد ايه اللي هيتغير وايه اللي هيتحذف وايه اللي هيفضل",
        "مثلا لو البوست اللي هو باعته مكتوبه فيه رقم تلفون",
        "والشركه لها رقم تلفون ومش هم هم قول غير رقم التلفون اللي موجود برقم تلفون الشركه",
        "لو الشركه مش لها رقم تلفون يبقا حط في اللي هيتحذف رقم التلفون",
        "وهكذا",
        "وقول ايه اللي هيفضل",
        "مثلا لو في الحاجات معينه في الخلفيه شايف انها المفروض تكون تبع ال templet قول انها لازم تفضل",
        "انت لازم تفضل بين المحتوي الكريتيف اللي بيتغير كل مره والمحتوي اللي ثابت علطول",
        "وفي الحاجات اللي هتفضل او هتتغير لازم توضح مكانها فين فوق يمين او تحت يسار ..",
        "بص ال keep, change, remove دي لازم توضح فيها كل حاجه لا تترك اي شيء حتي لو صغير للصدفه",
        "لازم توضح ان ال templet هيكون خالي من اي محتوي يعني لا تكتب اي شيء في ال templet انا عايزه فاضي خالص",
        "لو مش نفس الشركه لازم كل معلومات التواصل تقول انها تتغير او تتحذف لا تترك اي شيء من البوست القديم",
    ]
    return "\n".join(prompt)


def template_analysis_user_prompt(company: dict) -> str:
    prompt = [
        "## Company Profile",
        f"- Name: {company.get("company_name", "")}",
        f"- Industry: {company.get("industry", "")}",
        f"- Description: {company.get("description", "")}",
        f"- Mission and Goal: {company.get("mission_and_goal", "")}",
        f"- Brand Tone: {company.get("brand_tone", "")}",
        f"- Target Audience: {company.get("target_audience", "")}",
        f"- Locale: {company.get("language_and_locale", "")}",
        f"- Brand Colors: {company.get("brand_color", "")}",
        f"- Visual Style: {company.get("visual_style", "")}",
        f"- Visual Constraints: {company.get("visual_constraints", "")}",
        f"- Main Character: {company.get("main_character_name", "")} (Is Character: {company.get("is_character", "")})",
        f"- Character Constraints: {company.get("main_character_constraints", "")}",
        f"- Character Image: {company.get("main_character_image_url", "")}",
        f"- Website: {company.get("website_url", "")}",
        f"- Social Media Username: {company.get("social_media_username", "")}",
        f"- Facebook: {company.get("facebook_url", "")}",
        f"- X (Twitter): {company.get("x_url", "")}",
        f"- Instagram: {company.get("instagram_url", "")}",
        f"- LinkedIn: {company.get("linkedin_url", "")}",
        f"- TikTok: {company.get("tiktok_url", "")}",
        f"- General Constraints: {company.get("constraints", "")}",
    ]
    return "\n".join(prompt)


def template_creation_from_prompt_system_prompt() -> str:
    prompt = [
        "بص انت مصمم جرافيك محترف ومبدع",
        "دورك عمل تصميم templet للسوشيال ميديا بناء على طلب المستخدم",
        "اليوزر هيبعت لك وصف للتصميم اللي هو عايزه او تخيله ليه",
        "وهيبعت لك شعار الشركه ومعلومات عنها",
        "لازم التصميم يكون احترافي جدا ويناسب هوية الشركه",
        "والاهم ان ده templet يعني لازم يكون فاضي من اي محتوي نصي او صور",
        "صمم الخلفية والاماكن الفاضية وتوزيع العناصر (شعار، تذييل، هيدر) بشكل متناسق",
        "ممنوع تحط اي كلام او صور اشخاص او منتجات، فقط اماكن فاضية ليهم",
        "التصميم لازم يكون clean و professional",
    ]
    return "\n".join(prompt)


def template_creation_from_prompt_user_prompt(company: dict, user_request: str) -> str:
    prompt = [
        "## User Request",
        f"{user_request}",
        "",
        "## Company Profile",
        f"- Name: {company.get("company_name", "")}",
        f"- Industry: {company.get("industry", "")}",
        f"- Description: {company.get("description", "")}",
        f"- Mission: {company.get("mission_and_goal", "")}",
        f"- Tone: {company.get("brand_tone", "")}",
        f"- Audience: {company.get("target_audience", "")}",
        f"- Colors: {company.get("brand_color", "")}",
        f"- Style: {company.get("visual_style", "")}",
        f"- Constraints: {company.get("constraints", "")} {company.get("visual_constraints", "")}",
        f"- Character: {company.get("main_character_name", "") if company.get("is_character", "") else 'None'}",
        f"- Socials: {company.get("social_media_username", "")}",
    ]
    return "\n".join(prompt)


def template_generation_system_prompt() -> str:
    prompt = [
        "بص انت اداه توليد templets for social media",
        "اليوزر هيبعت لك logo بتاع شركته وال post اللي عايز يعمل زيه والملاحظات للحاجات اللي عايز يغيرها ويعدلها ويحذها",
        "دورك عمل templet فاضي تماما",
        "ولازم يكون في شعار واضح",
        "ال templet اللي هتعمله ده هيتم استخدامه علطول بعدين فخليك مركز وانت بتعمل كل تفصيله",
        "لو في مكان لكلام او صوره خليه فاضي خالص عشان ده templet فلازم يكون خالي من اي شيء",
        "حتي لازم يكون خالص من اي خلفيه",
        "بشكل اساسي لازم يكون خالي من الخلفيه واي عناصر او اشخاص",
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
        f"Company: {company.get("company_name", "")}",
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
