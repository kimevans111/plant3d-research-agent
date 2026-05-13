"""Shared dataclasses for the lightweight Skill Layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SkillTraceStep:
    """One observable step in skill selection or execution."""

    step: str
    status: str
    output_summary: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass
class SkillError:
    """Structured skill error information."""

    code: str
    message: str
    recoverable: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass
class SkillDefinition:
    """Loaded skill definition with Markdown instructions and JSON schema."""

    name: str
    version: str
    description: str
    skill_dir: Path
    skill_md_path: Path
    schema_path: Path
    schema: dict[str, Any]
    skill_md: str
    recommended_tools: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        """Return a concise public summary of the skill definition."""
        return {
            "skill_name": self.name,
            "version": self.version,
            "description": self.description,
            "recommended_tools": self.recommended_tools,
            "categories": self.categories,
        }


@dataclass
class SkillInput:
    """Input accepted by the skill executor."""

    query: str
    file_paths: list[str] = field(default_factory=list)
    task_type: str | None = None


@dataclass
class SkillSelection:
    """Rule-based skill selection result."""

    skill_name: str
    confidence: float
    reason: str
    matched_rules: list[str] = field(default_factory=list)


@dataclass
class SkillOutput:
    """Output returned by the lightweight skill executor."""

    selected_skill: str
    confidence: float
    reason: str
    recommended_tools: list[str]
    trace: list[SkillTraceStep]
    error: SkillError | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        payload = {
            "selected_skill": self.selected_skill,
            "confidence": self.confidence,
            "reason": self.reason,
            "recommended_tools": self.recommended_tools,
            "trace": [step.to_dict() for step in self.trace],
        }
        if self.error:
            payload["error"] = self.error.to_dict()
        return payload
