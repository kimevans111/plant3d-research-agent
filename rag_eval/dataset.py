"""Dataset loading utilities for RAG-Eval Mini."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "id",
    "question",
    "expected_keywords",
    "expected_sources",
    "expected_answer_points",
    "category",
}


@dataclass(slots=True)
class EvalQuestion:
    """One RAG evaluation question with lightweight expected evidence."""

    id: str
    question: str
    expected_keywords: list[str]
    expected_sources: list[str]
    expected_answer_points: list[str]
    category: str

    @classmethod
    def from_dict(cls, data: dict[str, Any], line_no: int | None = None) -> "EvalQuestion":
        """Create and validate an evaluation question from a JSON object."""
        missing = sorted(REQUIRED_FIELDS - set(data))
        location = f" on line {line_no}" if line_no is not None else ""
        if missing:
            raise ValueError(f"Eval question{location} is missing required fields: {', '.join(missing)}")

        list_fields = ["expected_keywords", "expected_sources", "expected_answer_points"]
        for field_name in list_fields:
            value = data[field_name]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"Eval question{location} field '{field_name}' must be a list of strings.")

        for field_name in ["id", "question", "category"]:
            if not isinstance(data[field_name], str) or not data[field_name].strip():
                raise ValueError(f"Eval question{location} field '{field_name}' must be a non-empty string.")

        return cls(
            id=data["id"].strip(),
            question=data["question"].strip(),
            expected_keywords=[item.strip() for item in data["expected_keywords"] if item.strip()],
            expected_sources=[Path(item).name for item in data["expected_sources"] if item.strip()],
            expected_answer_points=[item.strip() for item in data["expected_answer_points"] if item.strip()],
            category=data["category"].strip(),
        )


def load_eval_questions(path: str | Path) -> list[EvalQuestion]:
    """Load a JSONL evaluation dataset and return validated questions."""
    eval_path = Path(path)
    if not eval_path.exists() or not eval_path.is_file():
        raise FileNotFoundError(f"Eval file not found: {eval_path}")

    questions: list[EvalQuestion] = []
    for line_no, raw_line in enumerate(eval_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_no}: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"Eval question on line {line_no} must be a JSON object.")
        questions.append(EvalQuestion.from_dict(data, line_no=line_no))

    if not questions:
        raise ValueError(f"Eval file contains no questions: {eval_path}")
    return questions
