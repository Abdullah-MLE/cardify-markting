AGENTS.md — Global Agent Rules for Cardify Marketing
This file is read by every AI agent (LLM call) in the system. It defines the shared rules.

Project Overview
Cardify Marketing is a social-media content management system that uses AI to generate posts, stories, carousels, templates, and weekly content plans for companies.

Architecture

Backend: Python (FastAPI or Streamlit)

Database: Supabase (PostgreSQL) — companies, weekly_plans, content, templates tables

AI Model: Google Gemini via the google-genai SDK

Prompt System: Python-based architecture — every prompt lives in `services/prompts/` as Python strings/functions.

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

All prompts are loaded via `services.prompts` — hardcoded in Python functions.

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

✅ Read the appropriate prompt file in `services/prompts/` before every call — it contains the rules

✅ Pass the full company context (name, industry, brand_tone, target_audience, language_and_locale, brand_color, visual_style, visual_constraints, constraints, is_character, main_character_name, main_character_constraints) to every call

✅ Use the Gemini retry logic in GeminiWrapper for all API calls

✅ Set response_mime_type = "application/json" and response_schema = <Pydantic class> for text skills

✅ Set the image aspect ratio via ImageParams.output_image_aspect_ratio for image skills

✅ Handle errors in the UI with clear messages

DON'T

❌ Don't return text when the schema expects JSON

❌ Don't return a single string when the schema expects a list

❌ Don't use mock data or time.sleep() to fake AI latency

❌ Don't commit .env, gcp-key.json, or any secret to version control

❌ Don't put emojis in any output

File Organization
```text
project/

├── AGENTS.md                          ← you are here

├── services/

│   ├── prompts/                       ← contains all the python-based prompts
│   │   ├── single_post_prompts.py
│   │   ├── ...

│   ├── ai_service.py                  ← high-level: takes a skill_name + context and maps to prompts

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

How to Modify the Project (Agent Guide)
---------------------------------------
If you are an AI Agent working on this project, follow this guide to make modifications quickly without reading the entire repository:

1. Adding/Editing Prompts:
   - Go to services/prompts/.
   - All prompts are Python functions returning strings.
   - If you need to modify the prompt for Image Generation, go to services/prompts/image_prompts.py.
   - To add a new skill prompt, create or append to the appropriate .py file, then update services/ai_service.py to route the new skill_name to your new function.

2. Adding a New Feature Tab:
   - Create a new file in 	abs/ (e.g., 	abs/my_new_tab.py).
   - Implement a 
ender(company_id) function using Streamlit (st.).
   - Import and add your new tab to pp.py in the navigation setup.

3. Database Changes:
   - Supabase CRUD operations are handled through libs/SupabaseCRUD/.
   - If you need to fetch or upload images, use libs.SupabaseCRUD.db_services.upload_image.

4. Image Generation / Media:
   - The AI generates images via Gemini 2.0 Flash. 
   - All image results from AI are bytes. Use PIL.Image to convert them to WebP and upload them to Supabase before displaying to the user, as the application relies on Supabase URLs for persistent storage.

