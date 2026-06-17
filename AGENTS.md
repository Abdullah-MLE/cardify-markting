AGENTS.md — Global Agent Rules for CampaignGenius / Tansiq AI
This file is read by every AI agent (LLM call) in the system. It defines the shared rules. Per-task rules live in skills/<skill_name>/skill.md.

Project Overview
CampaignGenius (also called Tansiq AI) is a social-media content management system that uses AI to generate posts, stories, carousels, templates, and weekly content plans for companies.

Architecture

Backend: Python (FastAPI or Streamlit)

Database: Supabase (PostgreSQL) — companies, weekly_plans, content, templates tables

AI Model: Google Gemini via the google-genai SDK

Prompt System: Skills-based architecture — every prompt lives in skills/<skill_name>/ as Markdown + Jinja2, never as Python strings

Skill File Format
Each skill in skills/<skill_name>/ contains:

File	Purpose
skill.md	System prompt — Role, Task, Rules, Output. Read first.
user_context.md	User prompt template — Jinja2 placeholders like {{ company.company_name }}. Rendered with the call's context.
schema.json	JSON output schema — for text-generation skills only. The Gemini call uses this to force structured output.
examples.md	Few-shot examples — appended to the user prompt to improve quality.
Skills live in ONE directory, in ONE repo. Don't duplicate.

The 10 Skills
Skill	Type	Output
analyze_company	Text	JSON CompanyProfile
analyze_template	Text (multimodal)	JSON TemplateAnalysis
create_weekly_plan	Text	JSON WeeklyPlanGeneration
generate_day_content	Text	JSON DayContentGeneration
generate_post	Text	JSON SinglePostGeneration (content_type=post)
generate_story	Text	JSON SinglePostGeneration (content_type=story)
generate_carousel	Text	JSON CarouselGeneration
generate_image	Image	PNG/JPEG bytes
edit_image	Image (inpaint)	PNG/JPEG bytes
generate_template	Image	PNG/JPEG bytes (blank canvas)
Code Standards

Python 3.10+

Type hints on every function signature

Pydantic models for all structured AI responses

All prompts are loaded via services/prompt_loader.py — never hardcoded in Python

Logging via app/core/logging.py

Universal AI Content Rules
These apply to every text generation call. Individual skills can extend, but not contradict.

1.
Language split for bilingual tasks:

Headlines, captions, body text → in the company's language_and_locale.

Visual descriptions (post_idea) → ALWAYS in English, regardless of the company's language.

2.
NO emojis anywhere in any output. Strip them.
3.
Output is JSON only for text skills. No markdown fences, no prose around it.
4.
null for unknowns — never use "" or "N/A". Pydantic models treat null differently from missing.
5.
Aspect ratio must be one of "1:1", "3:4", "4:3", "9:16", "16:9". No other values.
6.
Schema strictness — if a schema requires minItems: 1, the model must produce at least 1. Don't return empty arrays unless the field allows it.
Do / Don't
DO

✅ Read the skill's skill.md before every call — it contains the rules

✅ Pass the full company context (name, industry, brand_tone, target_audience, language_and_locale, brand_color, visual_style, visual_constraints, constraints, is_character, main_character_name, main_character_constraints) to every call

✅ Use the Gemini retry logic in GeminiWrapper for all API calls

✅ Render the user prompt with Jinja2 from user_context.md and pass real data — never leave {{ }} placeholders unfilled

✅ Append examples.md content to the user prompt before sending (it improves quality significantly)

✅ Set response_mime_type = "application/json" and response_schema = <Pydantic class> for text skills

✅ Set the image aspect ratio via ImageParams.output_image_aspect_ratio for image skills

✅ Handle errors in the UI with clear messages

DON'T

❌ Don't hardcode prompts in Python files

❌ Don't duplicate prompts across files — the skills/ directory is the single source of truth

❌ Don't put the company's language_and_locale text in post_idea (always English)

❌ Don't return text when the schema expects JSON

❌ Don't return a single string when the schema expects a list

❌ Don't use mock data or time.sleep() to fake AI latency

❌ Don't commit .env, gcp-key.json, or any secret to version control

❌ Don't put emojis in any output

File Organization
```text
project/

├── AGENTS.md                          ← you are here

├── skills/

│   ├── analyze_company/

│   │   ├── skill.md

│   │   ├── user_context.md

│   │   ├── schema.json

│   │   └── examples.md

│   ├── analyze_template/

│   ├── create_weekly_plan/

│   ├── generate_day_content/

│   ├── generate_post/

│   ├── generate_story/

│   ├── generate_carousel/

│   ├── generate_image/

│   ├── edit_image/

│   └── generate_template/

```
├── services/

│   ├── ai_service.py                  ← high-level: takes a skill_name + context

│   ├── prompt_loader.py               ← loads skill.md, user_context.md, examples.md

│   └── ... (other services)

├── libs/

│   ├── GeminiWrapper/                 ← low-level Gemini SDK wrapper

│   └── SupabaseCRUD/                  ← database access

├── schemas/                           ← Pydantic models matching the schemas

└── app/

    ├── api/                           ← FastAPI routes

    └── core/

        ├── config.py

        └── logging.py
```
