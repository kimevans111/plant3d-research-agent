from pathlib import Path

from skills.executor import SkillExecutor
from skills.registry import SkillRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_executor_returns_selected_skill_and_trace() -> None:
    executor = SkillExecutor(registry=SkillRegistry(ROOT / "skills"))

    result = executor.execute("运行 RAG-Eval 看 source_hit@k", task_type=None)
    payload = result.to_dict()

    assert payload["selected_skill"] == "rag_evaluation"
    assert payload["recommended_tools"]
    assert payload["trace"]


def test_executor_fallback_for_unknown_query() -> None:
    executor = SkillExecutor(registry=SkillRegistry(ROOT / "skills"))

    result = executor.execute("帮我看看这个问题")

    assert result.selected_skill in {"rag_research_qa", "plant3d_domain_explanation"}
    assert result.confidence > 0
    assert result.trace
