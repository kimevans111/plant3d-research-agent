from skills.selector import SkillSelector


def test_selects_training_log_analysis_for_training_question() -> None:
    result = SkillSelector().select("为什么我的 F1 后期震荡？", file_paths=["run.log"])

    assert result.skill_name == "training_log_analysis"
    assert result.confidence >= 0.8


def test_selects_rag_evaluation_for_eval_question() -> None:
    result = SkillSelector().select("运行 RAG-Eval 看 citation hit 是否可靠")

    assert result.skill_name == "rag_evaluation"


def test_selects_rag_research_qa_for_document_question() -> None:
    result = SkillSelector().select("这篇论文笔记里的依据和 citation 在哪里？")

    assert result.skill_name == "rag_research_qa"


def test_selects_report_generation_for_report_question() -> None:
    result = SkillSelector().select("请生成 Markdown 报告并导出")

    assert result.skill_name == "report_generation"


def test_selects_domain_explanation_for_plant3d_question() -> None:
    result = SkillSelector().select("Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？")

    assert result.skill_name == "plant3d_domain_explanation"
