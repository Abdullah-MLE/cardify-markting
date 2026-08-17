# AgenticAI API Documentation

**Base URL:** `http://72.62.226.82:8000/api/v1`

---

## 1. Companies

### Actions

#### `POST /companies/extract`

Scrapes a website and extracts company information using AI.

**Request Body:**

```json
{
    "url": "https://example.com"
}
```

**Response:** `Company` object (see [Models](#models)).

---

### CRUD

#### `GET /companies/{company_id}`

Returns a `Company` object by ID.

#### `POST /companies`

Creates a new company record.

**Request Body:** `Company` object (without `id`).

**Response:**

```json
{
    "id": 1
}
```

#### `PUT /companies/{company_id}`

Updates an existing company.

**Request Body:** `Company` object (partial or full).

**Response:** Updated `Company` object.

---

## 2. Templates

### Actions

#### `POST /templates/create`

Creates a template using one of two flows:
- **From a post URL:** Analyzes the post, generates a blank template, and extracts constraints.
- **From a prompt:** Generates a template directly from a text description.

> At least one of `post_url` or `prompt` must be provided.

**Request Body:**

```json
{
    "company_id": 1,
    "post_url": "https://instagram.com/p/...",
    "prompt": "modern minimal template with logo at top-right"
}
```

| Field        | Type   | Required | Description                                                       |
|:-------------|:-------|:---------|:------------------------------------------------------------------|
| `company_id` | int    | Yes      | ID of the company                                                 |
| `post_url`   | string | No       | URL of an existing post to base the template on                   |
| `prompt`     | string | No       | Text description for template generation (or extra notes if URL)  |

**Response:**

```json
{
    "template_url": "https://storage.supabase.co/...",
    "constraints": "1. Logo is fixed at top-right..."
}
```

---

#### `POST /templates/edit`

Edits an existing template based on user notes.

**Request Body:**

```json
{
    "template_id": 1,
    "notes": "change background color to dark blue"
}
```

| Field         | Type   | Required | Description                 |
|:--------------|:-------|:---------|:----------------------------|
| `template_id` | int    | Yes      | ID of the template to edit  |
| `notes`       | string | Yes      | Edit instructions           |

**Response:**

```json
{
    "template_url": "https://storage.supabase.co/..."
}
```

---

### CRUD

#### `GET /templates/{template_id}`

Returns a `Template` object by ID.

#### `POST /templates`

Creates a new template record.

**Request Body:** `Template` object (without `id`, `created_at`).

**Response:** `{"id": 1}`

#### `PUT /templates/{template_id}`

Updates an existing template.

**Request Body:** `Template` object (partial or full).

---

## 3. Weekly Plans

### Actions

#### `POST /weekly-plans/create`

Generates a weekly marketing plan using AI.

**Request Body:**

```json
{
    "company_id": 1,
    "title": "Week 1 - Launch Campaign",
    "start_date": "2026-02-20",
    "end_date": "2026-02-27",
    "notes": "Focus on product awareness"
}
```

| Field        | Type   | Required | Default                        | Description                          |
|:-------------|:-------|:---------|:-------------------------------|:-------------------------------------|
| `company_id` | int    | Yes      | —                              | ID of the company                    |
| `title`      | string | No       | `"Weekly Plan {date}"`         | Title of the plan                    |
| `start_date` | string | No       | Today                          | Start date (YYYY-MM-DD)             |
| `end_date`   | string | No       | Start + 7 days                 | End date (YYYY-MM-DD)               |
| `notes`      | string | No       | `"just make a weekly plan"`    | Notes/instructions for the AI        |

**Response:** `WeeklyPlan` object (see [Models](#models)).

---

#### `POST /weekly-plans/edit`

Edits the content of an existing weekly plan using AI.

**Request Body:**

```json
{
    "weekly_plan_id": 1,
    "notes": "Add more focus on Instagram stories"
}
```

| Field            | Type   | Required | Description                        |
|:-----------------|:-------|:---------|:-----------------------------------|
| `weekly_plan_id` | int    | Yes      | ID of the weekly plan to edit      |
| `notes`          | string | Yes      | Edit instructions                  |

**Response:**

```json
{
    "ai_plan": "Updated plan text..."
}
```

---

### CRUD

#### `GET /weekly-plans/{plan_id}`

Returns a `WeeklyPlan` object by ID.

#### `POST /weekly-plans`

Creates a new weekly plan record.

**Request Body:** `WeeklyPlan` object (without `id`, `created_at`).

**Response:** `{"id": 1}`

#### `PUT /weekly-plans/{plan_id}`

Updates a weekly plan.

**Request Body:** `WeeklyPlan` object (partial or full).

---

## 4. Content

### Actions

#### `POST /content/create-single-post`

Creates a **complete post** (text + images) from a headline and notes in one call.
The AI determines the content type (`post`, `story`, or `carousel`) based on the notes. Defaults to `post`.

**Request Body:**

```json
{
    "company_id": 1,
    "template_id": 1,
    "h1": "Launch our new product line",
    "notes": "make it a carousel with 5 slides"
}
```

| Field         | Type   | Required | Default | Description                                              |
|:--------------|:-------|:---------|:--------|:---------------------------------------------------------|
| `company_id`  | int    | Yes      | —       | ID of the company                                        |
| `template_id` | int    | Yes      | —       | ID of the template to use for image generation           |
| `h1`          | string | Yes      | —       | Main headline / topic                                    |
| `notes`       | string | No       | `""`    | Instructions (e.g. "make it a carousel", "story format") |

**Response:**

```json
{
    "content_id": 42,
    "content_type": "post",
    "h1": ["Launch our new product line"],
    "caption": "Introducing our latest collection...",
    "post_images": ["https://storage.supabase.co/.../post-42-1708383600.png"],
    "post_idea": ["A vibrant product showcase with warm lighting"]
}
```

| Field          | Type         | Description                                                      |
|:---------------|:-------------|:-----------------------------------------------------------------|
| `content_id`   | int          | ID of the created content record in the database                 |
| `content_type` | string       | `"post"`, `"story"`, or `"carousel"` (determined by AI)          |
| `h1`           | list[string] | Headlines — 1 for post/story, multiple for carousel              |
| `caption`      | string       | Generated caption text                                           |
| `post_images`  | list[string] | Generated image URLs — 1 for post/story, multiple for carousel   |
| `post_idea`    | list[string] | Visual descriptions used to generate the images                  |

---

#### `POST /content/create-week`

Generates text content for all 7 days of the week (no images).

**Request Body:**

```json
{
    "weekly_plan_id": 1
}
```

| Field            | Type | Required | Description               |
|:-----------------|:-----|:---------|:--------------------------|
| `weekly_plan_id` | int  | Yes      | ID of the weekly plan     |

**Response:**

```json
{
    "days": [DayContentGeneration, ...]
}
```

Each `DayContentGeneration` contains a `content_list` of `ContentItem` objects (see [Models](#models)).

---

#### `POST /content/create-day`

Generates text content items for a specific day (no images).

**Request Body:**

```json
{
    "weekly_plan_id": 1,
    "day_order": 1,
    "day_name": "Monday",
    "date": "2026-02-20",
    "notes": "Focus on engagement"
}
```

| Field            | Type   | Required | Default      | Description                          |
|:-----------------|:-------|:---------|:-------------|:-------------------------------------|
| `weekly_plan_id` | int    | Yes      | —            | ID of the weekly plan                |
| `day_order`      | int    | Yes      | —            | Day number (1-7)                     |
| `day_name`       | string | Yes      | —            | Day name (e.g. "Monday")            |
| `date`           | string | Yes      | —            | Date (YYYY-MM-DD)                   |
| `notes`          | string | No       | `"no notes"` | Notes/instructions for the AI        |

**Response:** `DayContentGeneration` object.

---

#### `POST /content/create-image`

Generates image(s) for an existing content item based on its type.
- `post` → 1 image
- `story` → 1 image (9:16 aspect ratio)
- `carousel` → multiple images (cover + continuation slides)

**Request Body:**

```json
{
    "content_id": 1,
    "template_id": 1,
    "user_prompt": "add warm lighting"
}
```

| Field         | Type   | Required | Default | Description                           |
|:--------------|:-------|:---------|:--------|:--------------------------------------|
| `content_id`  | int    | Yes      | —       | ID of the content item                |
| `template_id` | int    | Yes      | —       | ID of the template to use             |
| `user_prompt` | string | No       | `null`  | Additional instructions for the AI    |

**Response:**

```json
{
    "result": "https://..." 
}
```

> For carousels, `result` is a list of URLs: `["url1", "url2", ...]`

---

#### `POST /content/edit-image`

Edits an existing content image based on user notes.

**Request Body:**

```json
{
    "content_id": 1,
    "notes": "make the background darker",
    "slide_index": 0
}
```

| Field         | Type | Required | Default | Description                                    |
|:--------------|:-----|:---------|:--------|:-----------------------------------------------|
| `content_id`  | int  | Yes      | —       | ID of the content item                         |
| `notes`       | str  | Yes      | —       | Edit instructions                              |
| `slide_index` | int  | No       | `null`  | Slide to edit (required for carousel type)     |

**Response:**

```json
{
    "result": "https://..."
}
```

---

### CRUD

#### `GET /content/{content_id}`

Returns a `Content` object by ID.

#### `POST /content`

Creates a new content record manually.

**Request Body:** `Content` object (without `id`, `created_at`).

**Response:** `{"id": 1}`

#### `PUT /content/{content_id}`

Updates an existing content record.

**Request Body:** `Content` object (partial or full).

---

## 5. Health Check

#### `GET /`

**Response:** `{"message": "AgenticAI API is running"}`

#### `GET /health`

**Response:** `{"status": "healthy"}`

> These two endpoints are NOT prefixed with `/api/v1`.

---

## Models

### Database Models

#### Company

```json
{
    "company_name": "string",
    "industry": "string",
    "description": "string",
    "mission_and_goal": "string",
    "brand_tone": "string",
    "target_audience": "string",
    "language_and_locale": "string",
    "constraints": "string",
    "is_character": false,
    "main_character_name": "string",
    "main_character_constraints": "string",
    "main_character_image_url": "string",
    "visual_constraints": "string",
    "visual_style": "string",
    "brand_color": "string",
    "logo_url": "string",
    "website_url": "string",
    "social_media_username": "string",
    "facebook_url": "string",
    "x_url": "string",
    "instagram_url": "string",
    "linkedin_url": "string",
    "tiktok_url": "string"
}
```

---

#### Template

```json
{
    "id": 1,
    "created_at": "2026-02-20T00:00:00",
    "company_id": 1,
    "template_url": "https://storage.supabase.co/...",
    "template_constraints": "1. Logo is fixed...",
    "source_post_url": "https://instagram.com/p/...",
    "is_source_same_company": false,
    "aspect_ratio": "3:4"
}
```

| Field                    | Type   | Required | Default | Description                                   |
|:-------------------------|:-------|:---------|:--------|:----------------------------------------------|
| `id`                     | int    | Auto     | —       | Auto-generated                                |
| `created_at`             | string | Auto     | —       | Auto-generated                                |
| `company_id`             | int    | Yes      | —       | Owner company                                 |
| `template_url`           | string | No       | `null`  | URL of the generated template image           |
| `template_constraints`   | string | No       | `null`  | Usage rules for the template                  |
| `source_post_url`        | string | No       | `null`  | Original post used as reference               |
| `is_source_same_company` | bool   | No       | `false` | Whether the source post is from same company  |
| `aspect_ratio`           | string | No       | `null`  | Aspect ratio (e.g. "1:1", "3:4", "9:16")     |

---

#### WeeklyPlan

```json
{
    "company_id": 1,
    "plan_title": "Week 1 - Launch",
    "start_date": "2026-02-20",
    "end_date": "2026-02-27",
    "ai_plan": "Day 1: Focus on awareness...",
    "status": "draft"
}
```

| Field          | Type   | Required | Default | Description                       |
|:---------------|:-------|:---------|:--------|:----------------------------------|
| `company_id`   | int    | Yes      | —       | Owner company                     |
| `plan_title`   | string | Yes      | —       | Plan title                        |
| `start_date`   | string | No       | `null`  | Start date (YYYY-MM-DD)          |
| `end_date`     | string | No       | `null`  | End date (YYYY-MM-DD)            |
| `ai_plan`      | string | No       | `null`  | AI-generated plan text            |
| `status`       | string | No       | `null`  | Plan status                       |

---

#### Content

The unified content model for posts, stories, and carousels.

```json
{
    "id": 1,
    "created_at": "2026-02-20T00:00:00",
    "company_id": 1,
    "week_id": 1,
    "content_type": "post",
    "publish_date": "2026-02-21",
    "publish_time": "14:00",
    "publish_day": "Saturday",
    "status": "draft",
    "h1": ["Main Headline"],
    "caption": "Post caption text...",
    "post_images": ["https://storage.supabase.co/..."],
    "post_idea": ["A vibrant product showcase..."],
    "use_character": [false]
}
```

| Field           | Type         | Required | Default | Description                                                      |
|:----------------|:-------------|:---------|:--------|:-----------------------------------------------------------------|
| `id`            | int          | Auto     | —       | Auto-generated                                                   |
| `created_at`    | string       | Auto     | —       | Auto-generated                                                   |
| `company_id`    | int          | Yes      | —       | Owner company                                                    |
| `week_id`       | int          | Yes      | —       | Associated weekly plan ID (0 for standalone posts)               |
| `content_type`  | string       | No       | `post`  | `"post"`, `"story"`, or `"carousel"`                             |
| `publish_date`  | string       | No       | `null`  | Publish date (YYYY-MM-DD)                                        |
| `publish_time`  | string       | No       | `null`  | Publish time (HH:MM)                                             |
| `publish_day`   | string       | No       | `null`  | Day name                                                         |
| `status`        | string       | No       | `draft` | Content status                                                   |
| `h1`            | list[string] | No       | `[]`    | Headlines — 1 item for post/story, multiple for carousel slides  |
| `caption`       | string       | No       | `""`    | Caption text                                                     |
| `post_images`   | list[string] | No       | `[]`    | Generated image URLs — 1 for post/story, multiple for carousel   |
| `post_idea`     | list[string] | No       | `[]`    | Visual descriptions (used as prompts for image generation)       |
| `use_character` | list[bool]   | No       | `[]`    | Whether to use a character in each image                         |

---

### AI Response Models

These models are returned by AI generation endpoints (not stored directly in DB).

#### ContentItem

A single content piece within a day's generation.

```json
{
    "type": "post",
    "headlines": ["Main Headline"],
    "post_ideas": ["Visual description..."],
    "use_character": [false],
    "posting_hour": 14,
    "caption": "Caption text..."
}
```

#### DayContentGeneration

Container for all content items generated for a specific day.

```json
{
    "content_list": [ContentItem, ...]
}
```

#### SinglePostGeneration

AI response for `/create-single-post`. Used internally to build a `Content` object.

```json
{
    "content_type": "post",
    "headlines": ["Main Headline"],
    "post_ideas": ["Visual description..."],
    "caption": "Caption text...",
    "use_character": [false]
}
```

#### TempletAnalysis

Result of template analysis (used internally during template creation).

```json
{
    "is_same_company": false,
    "aspect_ratio": "3:4",
    "change": ["phone number", "address"],
    "keep": ["logo position", "background pattern"],
    "remove": ["old watermark"]
}
```

#### EditResponse

Result of post edit classification (used internally).

```json
{
    "edit_mode": "text",
    "text_changes": [{"field": "caption", "value": "new caption"}],
    "visual_changes": []
}
```
