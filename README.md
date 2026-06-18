# Cardify Marketing

Welcome to **Cardify Marketing** (also known as Cardify Marketing)! This is a powerful, AI-driven social media content management system designed to generate posts, stories, carousels, templates, and weekly content plans for companies.

## 🌟 Overview

Cardify Marketing streamlines the social media workflow by integrating advanced AI capabilities. It helps businesses automate and manage their daily social content with a beautiful and interactive user interface.

## 🏗️ Architecture

The project is built with modern, scalable technologies and follows a strict, modular architecture:

- **Frontend & Backend Framework:** [Streamlit](https://streamlit.io/) (Python 3.10+)
- **Database:** [Supabase](https://supabase.com/) (PostgreSQL)
- **AI Model:** Google Gemini (via `google-genai` SDK)
- **Prompt System:** A "Skills-based" architecture using Markdown + Jinja2 templates.

### Directory Structure

- `app.py`: The main entry point of the Streamlit application. It manages navigation and layout.
- `skills/`: The core of the AI logic. Each AI capability (e.g., generating a post, analyzing a company) is encapsulated as a "skill" containing its system prompt, user context template, and output schema.
- `schemas/`: Pydantic models to ensure that structured AI outputs strictly follow expected JSON schemas.
- `services/`: Business logic and orchestration layers:
  - `ai_service.py`: High-level AI operations.
  - `prompt_loader.py`: Loads the Markdown and Jinja2 templates from the `skills/` directory.
  - `db_services.py`: Database queries and management.
- `libs/`: Low-level integrations and wrappers:
  - `GeminiWrapper/`: Google Gemini SDK wrapper with built-in retry logic.
  - `SupabaseClient/`: Supabase database connection and CRUD operations.
- `tabs/`: Individual Streamlit UI pages (e.g., Planner, Studio, Dashboard).

## 🚀 Key Features

- **AI Content Generation:** Uses Google Gemini to dynamically create engaging posts, stories, and carousels.
- **Skills-Based Prompts:** All prompts are separated from code. They live in the `skills/` folder, ensuring clean code and highly tunable AI performance.
- **Structured JSON Output:** AI text responses are strictly enforced into JSON using Pydantic schemas.
- **Multilingual Support:** Content can be generated in the company's specific language and locale, while internal reasoning (like visual descriptions) remains in English.
- **Visual Studio:** Generate, edit, and analyze images and templates directly within the application.

## 🛠️ Setup & Installation

1. **Clone the repository.**
2. **Ensure Python 3.10+ is installed.**
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   Create a `.env` file in the root directory and add the following keys:
   ```env
   SUPABASE_URL="your_supabase_url"
   SUPABASE_KEY="your_supabase_key"
   GCP_PROJECT_ID="your_gcp_project_id"
   GCP_LOCATION="us-central1"
   GOOGLE_APPLICATION_CREDENTIALS="gcp-key.json"
   ```
   *Make sure you have your GCP service account JSON key saved as `gcp-key.json`.*

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 📜 Coding Standards & Rules

- **Type Hints:** All function signatures must use Python type hints.
- **Pydantic Models:** Always use Pydantic for structured AI responses.
- **No Hardcoded Prompts:** Prompts must only reside in the `skills/` directory.
- **Strict Schemas:** Always handle strict outputs, handling `null` instead of empty strings when data is unknown.
- **No Emojis in Output:** Emojis are strictly stripped from all generated content as per global rules.

Enjoy creating brilliant campaigns with **Cardify Marketing**!
