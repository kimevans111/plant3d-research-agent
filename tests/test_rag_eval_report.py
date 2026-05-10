from pathlib import Path

from rag_eval.report import generate_markdown_report


def test_generate_markdown_report_contains_required_sections(tmp_path: Path) -> None:
    result = {
        "summary": {
            "num_questions": 1,
            "source_hit_at_k": 1.0,
            "keyword_recall": 0.5,
            "citation_hit": 1.0,
            "answer_point_coverage": 0.5,
            "retrieval_empty_rate": 0.0,
            "average_score": 0.75,
        },
        "items": [
            {
                "id": "q1",
                "question": "Why?",
                "category": "method",
                "expected_sources": ["sample_paper_notes.md"],
                "retrieved_sources": ["sample_paper_notes.md"],
                "missing_keywords": ["boundary"],
                "failure_reason": None,
                "source_hit_at_k": 1.0,
                "keyword_recall": 0.5,
                "citation_hit": 1.0,
                "answer_point_coverage": 0.5,
                "average_score": 0.75,
                "retrieved_preview": ["Plant-GeoAT context"],
            }
        ],
    }

    report = generate_markdown_report(
        result=result,
        output_dir=tmp_path,
        retriever_type="keyword",
        top_k=3,
        use_agent_answer=False,
        mock_provider=True,
        timestamp="20260101_000000",
    )

    text = Path(report).read_text(encoding="utf-8")
    assert "Summary Metrics" in text
    assert "Failure Cases" in text
    assert "Detailed Results" in text
