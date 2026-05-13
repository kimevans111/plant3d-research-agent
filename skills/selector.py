"""Rule-based skill selector for Plant3D Research Agent."""

from __future__ import annotations

from pathlib import Path

from skills.schemas import SkillSelection


class SkillSelector:
    """Select the best skill using transparent keyword rules."""

    TASK_TYPE_MAP = {
        "log_analysis": "training_log_analysis",
        "report_generation": "report_generation",
        "doc_qa": "rag_research_qa",
        "rag_eval": "rag_evaluation",
        "domain_explanation": "plant3d_domain_explanation",
    }

    TRAINING_TERMS = {
        "training",
        "train",
        "log",
        "loss",
        "miou",
        "f1",
        "epoch",
        "overfit",
        "overfitting",
        "oscillation",
        "fluctuation",
        "震荡",
        "过拟合",
        "训练",
        "调参",
        "类别不平衡",
        "stem iou",
        "leaf iou",
    }
    RAG_EVAL_TERMS = {
        "rag-eval",
        "rag eval",
        "rag 评估",
        "source_hit",
        "source hit",
        "citation hit",
        "answer point",
        "top_k",
        "top-k",
        "failure case",
        "retrieval empty",
        "检索效果",
        "评估集",
        "命中率",
    }
    RAG_QA_TERMS = {
        "rag",
        "retrieval",
        "retrieve",
        "citation",
        "source",
        "paper",
        "document",
        "notes",
        "文档",
        "笔记",
        "论文",
        "依据",
        "来源",
        "检索",
        "引用",
    }
    REPORT_TERMS = {
        "report",
        "markdown",
        "export",
        "summary",
        "write up",
        "报告",
        "导出",
        "总结",
        "复盘",
    }
    DOMAIN_TERMS = {
        "plant-geoat",
        "leaf-stem",
        "thin stem",
        "point cloud",
        "segmentation",
        "phenotyping",
        "miou",
        "f1",
        "precision",
        "recall",
        "oa",
        "stem",
        "leaf",
        "boundary confusion",
        "点云",
        "表型",
        "叶片",
        "茎",
        "分割",
        "株高",
    }

    def select(
        self,
        query: str,
        file_paths: list[str] | None = None,
        task_type: str | None = None,
    ) -> SkillSelection:
        """Select a skill for the given query and optional files."""
        normalized = " ".join(query.lower().split())
        suffixes = {Path(path).suffix.lower() for path in file_paths or []}
        has_training_file = bool(suffixes & {".log", ".txt", ".csv", ".json"})

        if task_type and task_type in self.TASK_TYPE_MAP:
            skill_name = self.TASK_TYPE_MAP[task_type]
            return SkillSelection(
                skill_name=skill_name,
                confidence=0.95,
                reason=f"task_type explicitly maps to {skill_name}",
                matched_rules=[f"task_type:{task_type}"],
            )

        if self._contains_any(normalized, self.RAG_EVAL_TERMS):
            return SkillSelection(
                skill_name="rag_evaluation",
                confidence=0.9,
                reason="query mentions RAG evaluation, top-k, citation hit, or failure cases",
                matched_rules=["rag_eval_terms"],
            )

        if self._contains_any(normalized, self.TRAINING_TERMS) and (
            has_training_file or self._contains_any(normalized, {"震荡", "过拟合", "loss", "epoch", "f1", "miou", "调参"})
        ):
            return SkillSelection(
                skill_name="training_log_analysis",
                confidence=0.88 if has_training_file else 0.82,
                reason="query or file type points to training metrics and log diagnosis",
                matched_rules=["training_terms", "training_file" if has_training_file else "metric_terms"],
            )

        if self._contains_any(normalized, self.REPORT_TERMS):
            return SkillSelection(
                skill_name="report_generation",
                confidence=0.84,
                reason="query asks for Markdown/report/export style output",
                matched_rules=["report_terms"],
            )

        if self._contains_any(normalized, self.RAG_QA_TERMS):
            return SkillSelection(
                skill_name="rag_research_qa",
                confidence=0.83,
                reason="query asks for document-grounded retrieval, sources, or citations",
                matched_rules=["rag_qa_terms"],
            )

        if self._contains_any(normalized, self.DOMAIN_TERMS):
            return SkillSelection(
                skill_name="plant3d_domain_explanation",
                confidence=0.8,
                reason="query is about 3D plant point cloud segmentation domain concepts",
                matched_rules=["domain_terms"],
            )

        return SkillSelection(
            skill_name="rag_research_qa",
            confidence=0.55,
            reason="fallback to document-grounded QA when no stronger rule matches",
            matched_rules=["fallback"],
        )

    @staticmethod
    def _contains_any(text: str, terms: set[str]) -> bool:
        return any(term in text for term in terms)
