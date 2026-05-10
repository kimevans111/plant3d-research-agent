from pathlib import Path

from agent.research_agent import ResearchAgent


ROOT = Path(__file__).resolve().parents[1]


def test_why_question_with_log_file_routes_to_log_analysis() -> None:
    agent = ResearchAgent()

    task = agent.classify_task(
        "Why is stem IoU lower than leaf IoU?",
        [ROOT / "examples" / "sample_train.log"],
    )

    assert task == "log_analysis"


def test_doc_keyword_with_log_file_can_still_route_to_doc_qa() -> None:
    agent = ResearchAgent()

    task = agent.classify_task(
        "Use the paper notes and RAG to explain Plant-GeoAT.",
        [ROOT / "examples" / "sample_train.log"],
    )

    assert task == "doc_qa"


def test_why_question_with_log_file_runs_log_tools(tmp_path: Path) -> None:
    agent = ResearchAgent(
        reports_dir=tmp_path / "reports",
        figures_dir=tmp_path / "figures",
    )

    result = agent.run(
        query="Why is stem IoU lower than leaf IoU?",
        file_paths=[ROOT / "examples" / "sample_train.log"],
    )

    assert "parse_training_log" in result["used_tools"]
    assert "summarize_metrics" in result["used_tools"]
    assert result["parsed_log"]["best_miou"] is not None
    assert result["report_path"]
