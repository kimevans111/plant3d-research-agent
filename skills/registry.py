"""Skill registry for loading Markdown skill definitions and JSON schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skills.schemas import SkillDefinition


class SkillRegistry:
    """Load and validate local skill definitions from the skills directory."""

    REQUIRED_SCHEMA_FIELDS = {
        "skill_name",
        "version",
        "input_schema",
        "output_schema",
        "required_fields",
        "optional_fields",
        "error_schema",
    }

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).resolve().parent
        self._skills: dict[str, SkillDefinition] | None = None

    def list_skills(self) -> list[SkillDefinition]:
        """Return all loaded skills sorted by name."""
        return sorted(self._load_skills().values(), key=lambda item: item.name)

    def get_skill(self, name: str) -> SkillDefinition | None:
        """Return one loaded skill by name."""
        return self._load_skills().get(name)

    def validate_skill_schema(self, schema: dict[str, Any]) -> None:
        """Validate the minimal schema contract used by this project."""
        missing = self.REQUIRED_SCHEMA_FIELDS - set(schema)
        if missing:
            raise ValueError(f"Skill schema is missing required fields: {sorted(missing)}")
        if not isinstance(schema.get("skill_name"), str) or not schema["skill_name"]:
            raise ValueError("Skill schema field 'skill_name' must be a non-empty string.")
        if not isinstance(schema.get("input_schema"), dict):
            raise ValueError("Skill schema field 'input_schema' must be an object.")
        if not isinstance(schema.get("output_schema"), dict):
            raise ValueError("Skill schema field 'output_schema' must be an object.")
        if not isinstance(schema.get("required_fields"), list):
            raise ValueError("Skill schema field 'required_fields' must be a list.")
        if not isinstance(schema.get("optional_fields"), list):
            raise ValueError("Skill schema field 'optional_fields' must be a list.")
        if not isinstance(schema.get("error_schema"), dict):
            raise ValueError("Skill schema field 'error_schema' must be an object.")

    def _load_skills(self) -> dict[str, SkillDefinition]:
        if self._skills is not None:
            return self._skills

        skills: dict[str, SkillDefinition] = {}
        for skill_dir in self.root_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("__"):
                continue
            skill_md_path = skill_dir / "SKILL.md"
            schema_path = skill_dir / "schema.json"
            if not skill_md_path.exists() or not schema_path.exists():
                continue

            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON schema for skill '{skill_dir.name}': {exc}") from exc
            self.validate_skill_schema(schema)
            name = schema["skill_name"]
            skills[name] = SkillDefinition(
                name=name,
                version=str(schema.get("version", "0.1.0")),
                description=str(schema.get("description", "")),
                skill_dir=skill_dir,
                skill_md_path=skill_md_path,
                schema_path=schema_path,
                schema=schema,
                skill_md=skill_md_path.read_text(encoding="utf-8"),
                recommended_tools=list(schema.get("recommended_tools", [])),
                categories=list(schema.get("categories", [])),
            )

        self._skills = skills
        return skills
