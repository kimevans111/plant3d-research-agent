"""Lightweight skill executor.

The executor currently performs selection, loads the skill definition, and
returns the recommended tool plan. It intentionally avoids replacing the
existing Agent runtime.
"""

from __future__ import annotations

from pathlib import Path

from skills.registry import SkillRegistry
from skills.schemas import SkillError, SkillInput, SkillOutput, SkillTraceStep
from skills.selector import SkillSelector


class SkillExecutor:
    """Select a skill and return a traceable execution plan."""

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        selector: SkillSelector | None = None,
    ) -> None:
        self.registry = registry or SkillRegistry()
        self.selector = selector or SkillSelector()

    def execute(
        self,
        query: str,
        file_paths: list[str | Path] | None = None,
        task_type: str | None = None,
    ) -> SkillOutput:
        """Return selected skill, confidence, recommended tools, and trace."""
        skill_input = SkillInput(
            query=query,
            file_paths=[str(path) for path in file_paths or []],
            task_type=task_type,
        )
        trace = [
            SkillTraceStep(
                step="receive_input",
                status="success",
                output_summary=f"Received query with {len(skill_input.file_paths)} file path(s).",
            )
        ]

        selection = self.selector.select(
            query=skill_input.query,
            file_paths=skill_input.file_paths,
            task_type=skill_input.task_type,
        )
        trace.append(
            SkillTraceStep(
                step="select_skill",
                status="success",
                output_summary=f"Selected {selection.skill_name} using {', '.join(selection.matched_rules)}.",
            )
        )

        definition = self.registry.get_skill(selection.skill_name)
        if definition is None:
            trace.append(
                SkillTraceStep(
                    step="load_skill_definition",
                    status="error",
                    output_summary=f"Skill definition not found: {selection.skill_name}.",
                )
            )
            return SkillOutput(
                selected_skill=selection.skill_name,
                confidence=selection.confidence,
                reason=selection.reason,
                recommended_tools=[],
                trace=trace,
                error=SkillError(
                    code="skill_not_found",
                    message=f"Skill definition not found: {selection.skill_name}",
                    recoverable=True,
                ),
            )

        trace.append(
            SkillTraceStep(
                step="load_skill_definition",
                status="success",
                output_summary=f"Loaded {definition.name} v{definition.version}.",
            )
        )
        trace.append(
            SkillTraceStep(
                step="plan_tools",
                status="success",
                output_summary="Prepared recommended tools without executing the existing Agent.",
            )
        )

        return SkillOutput(
            selected_skill=selection.skill_name,
            confidence=selection.confidence,
            reason=selection.reason,
            recommended_tools=definition.recommended_tools,
            trace=trace,
        )
