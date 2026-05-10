from pathlib import Path

import pytest

from rag_eval.dataset import load_eval_questions


def test_load_eval_questions_jsonl(tmp_path: Path) -> None:
    eval_file = tmp_path / "eval.jsonl"
    eval_file.write_text(
        '{"id":"q1","question":"Why?","expected_keywords":["Plant-GeoAT"],'
        '"expected_sources":["notes.md"],"expected_answer_points":["geometry"],"category":"method"}\n',
        encoding="utf-8",
    )

    questions = load_eval_questions(eval_file)

    assert len(questions) == 1
    assert questions[0].id == "q1"
    assert questions[0].expected_sources == ["notes.md"]


def test_load_eval_questions_missing_field_error(tmp_path: Path) -> None:
    eval_file = tmp_path / "bad.jsonl"
    eval_file.write_text('{"id":"q1","question":"Why?"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="missing required fields"):
        load_eval_questions(eval_file)
