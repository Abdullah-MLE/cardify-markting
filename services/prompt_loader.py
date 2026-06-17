"""
Prompt loader for the skills-based architecture.

Each skill lives in `skills/<skill_name>/` and has:
- skill.md          → system prompt (Role / Task / Rules / Output)
- user_context.md   → user prompt template (Jinja2)
- schema.json       → optional JSON output schema (text skills)
- examples.md       → optional few-shot examples (appended to user prompt)

The loader reads these files and returns a single dict that the AI service
can hand to the GeminiWrapper.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, StrictUndefined, TemplateError


class PromptLoader:
    """Loads skill Markdown files from disk and renders them with Jinja2."""

    def __init__(self, skills_dir: Optional[str] = None) -> None:
        if skills_dir is None:
            import os

            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_dir = os.path.join(base, "skills")
        self.skills_dir = Path(skills_dir)
        # StrictUndefined raises if a {{ var }} isn't passed in, which is
        # exactly what we want — never let a missing variable leak into a prompt.
        self._env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_skill(self, skill_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load a skill by name and return rendered prompts, examples, and schema.

        Parameters
        ----------
        skill_name:
            Directory name under `skills/`.
        context:
            Template variables for Jinja2 rendering. Must contain every
            variable referenced in `user_context.md`.

        Returns
        -------
        dict with keys:
            - system_prompt: str (the rendered skill.md)
            - user_prompt:   str (rendered user_context.md + appended examples)
            - examples:      str (raw examples.md, "" if missing)
            - schema:        dict (parsed schema.json, None if missing)
        """
        skill_dir = self.skills_dir / skill_name
        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill '{skill_name}' not found at {skill_dir}")

        ctx = context or {}

        system_prompt = self._render(skill_dir / "skill.md", ctx)
        user_prompt = self._render(skill_dir / "user_context.md", ctx)

        # Examples are appended to the user prompt, not to the system prompt,
        # because they should appear close to the actual task.
        examples = ""
        examples_path = skill_dir / "examples.md"
        if examples_path.exists():
            examples = examples_path.read_text(encoding="utf-8")

        if examples:
            user_prompt = user_prompt.rstrip() + "\n\n# Examples (Few-Shot)\n\n" + examples

        # JSON schema for structured output (text skills only)
        schema = None
        schema_path = skill_dir / "schema.json"
        if schema_path.exists():
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {schema_path}: {exc}") from exc

        return {
            "system_prompt": system_prompt.strip(),
            "user_prompt": user_prompt.strip(),
            "examples": examples,
            "schema": schema,
        }

    def list_skills(self) -> list[str]:
        """List all available skill names (subdirectory names under `skills/`)."""
        if not self.skills_dir.exists():
            return []
        return sorted(
            d.name
            for d in self.skills_dir.iterdir()
            if d.is_dir() and (d / "skill.md").exists()
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render(self, path: Path, context: Dict[str, Any]) -> str:
        """Render a Markdown file with Jinja2. Returns empty string if missing."""
        if not path.exists():
            return ""
        try:
            template = self._env.from_string(path.read_text(encoding="utf-8"))
            return template.render(**context)
        except TemplateError as exc:
            raise ValueError(f"Failed to render template {path}: {exc}") from exc
