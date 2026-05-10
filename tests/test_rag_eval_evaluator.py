from pathlib import Path

from rag_eval.evaluator import RagEvaluator


def test_rag_evaluator_with_mock_retriever(tmp_path: Path) -> None:
    eval_file = tmp_path / "eval.jsonl"
    eval_file.write_text(
        '{"id":"q1","question":"Why does Plant-GeoAT help boundaries?",'
        '"expected_keywords":["Plant-GeoAT","local surface variation"],'
        '"expected_sources":["sample_paper_notes.md"],'
        '"expected_answer_points":["local surface variation"],'
        '"category":"method"}\n',
        encoding="utf-8",
    )

    def retrieve(query: str, top_k: int) -> list[dict[str, object]]:
        return [
            {
                "source": "sample_paper_notes.md",
                "chunk": "Plant-GeoAT uses local surface variation for boundary discrimination.",
                "score": 0.9,
            }
        ][:top_k]

    result = RagEvaluator(
        eval_file=eval_file,
        docs_dir=tmp_path,
        output_dir=tmp_path / "reports",
        retrieval_fn=retrieve,
        use_agent_answer=False,
    ).run()

    assert result["summary"]["num_questions"] == 1
    assert result["summary"]["source_hit_at_k"] == 1.0
    assert Path(result["detail_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert not result["failure_cases"]
