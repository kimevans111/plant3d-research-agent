from rag_eval.metrics import (
    answer_point_coverage,
    citation_hit,
    keyword_recall,
    source_hit_at_k,
)


def test_source_hit_at_k_matches_file_name() -> None:
    assert source_hit_at_k(["/tmp/sample_paper_notes.md"], ["sample_paper_notes.md"]) == 1
    assert source_hit_at_k(["sample_train.log"], ["sample_paper_notes.md"]) == 0


def test_keyword_recall_counts_phrase_hits() -> None:
    score = keyword_recall(
        ["leaf-stem boundary confusion", "local geometry", "missing term"],
        "Plant-GeoAT uses local geometry to reduce leaf stem boundary confusion.",
    )

    assert score == 2 / 3


def test_citation_hit_matches_expected_source() -> None:
    citations = [{"source": "sample_paper_notes.md", "chunk": "Plant-GeoAT"}]

    assert citation_hit(citations, ["sample_paper_notes.md"]) == 1
    assert citation_hit(citations, ["sample_metrics.csv"]) == 0


def test_answer_point_coverage() -> None:
    answer = "It uses local surface variation and relative position cues."

    assert answer_point_coverage(answer, ["local surface variation", "relative position"]) == 1.0
    assert answer_point_coverage(answer, ["local surface variation", "not present"]) == 0.5
