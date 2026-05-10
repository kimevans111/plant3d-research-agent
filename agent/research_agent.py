"""Research agent orchestration for Plant3D experiment analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from llm.provider import get_llm_provider
from rag.retriever import rag_retrieve_context
from tools.log_parser import parse_training_log
from tools.metric_analyzer import compare_models, summarize_metrics
from tools.plotter import generate_training_curve
from tools.report_generator import generate_markdown_report


class ResearchAgent:
    """A lightweight tool-calling agent for plant point cloud segmentation research."""

    def __init__(
        self,
        uploads_dir: str | Path = "uploads",
        reports_dir: str | Path = "reports",
        figures_dir: str | Path = "reports/figures",
    ) -> None:
        self.uploads_dir = Path(uploads_dir)
        self.reports_dir = Path(reports_dir)
        self.figures_dir = Path(figures_dir)
        self.llm = get_llm_provider()

    def run(
        self,
        query: str,
        file_paths: list[str | Path] | None = None,
        task_type: str | None = None,
    ) -> dict[str, Any]:
        """Run the agent and return a structured response."""
        paths = [Path(path) for path in file_paths or []]
        resolved_task = task_type or self.classify_task(query, paths)

        if resolved_task in {"log_analysis", "report_generation"}:
            return self._run_log_analysis(query, paths, make_report=True)
        if resolved_task == "model_compare":
            return self._run_model_compare(query, paths)
        if resolved_task == "doc_qa":
            return self._run_doc_qa(query)
        return self._run_general_advice(query)

    def classify_task(self, query: str, file_paths: list[Path]) -> str:
        """Classify a query into a coarse research task type."""
        lowered = query.lower()
        suffixes = {path.suffix.lower() for path in file_paths}
        has_log_file = bool(suffixes & {".log", ".txt"})
        if any(word in lowered for word in ["compare", "对比", "比较", "ranking", "rank"]):
            return "model_compare"
        if any(word in lowered for word in ["报告", "report", "总结实验"]) and has_log_file:
            return "report_generation"

        doc_keywords = ["论文", "paper", "document", "文档", "rag"]
        if has_log_file and not any(word in lowered for word in doc_keywords):
            return "log_analysis"

        if any(word in lowered for word in ["why", "为什么", *doc_keywords]):
            return "doc_qa"
        return "general_advice"

    def _candidate_log_paths(self, paths: list[Path]) -> list[Path]:
        if paths:
            return [path for path in paths if path.suffix.lower() in {".log", ".txt"} and path.exists()]
        return sorted(self.uploads_dir.glob("*.log")) + sorted(self.uploads_dir.glob("*.txt"))

    def _run_log_analysis(self, query: str, paths: list[Path], make_report: bool) -> dict[str, Any]:
        used_tools = ["parse_training_log", "summarize_metrics", "generate_training_curve"]
        log_paths = self._candidate_log_paths(paths)
        citations = self._retrieve_citations(query)
        if citations:
            used_tools.append("rag_retrieve_context")

        if not log_paths:
            return {
                "answer": "没有找到可分析的训练日志文件。请先上传 .log 或 .txt 日志，或在 file_paths 中指定日志路径。",
                "used_tools": used_tools,
                "citations": citations,
                "figures": [],
                "report_path": None,
            }

        parsed_results = [parse_training_log(path) for path in log_paths]

        figures: list[str] = []
        for parsed, log_path in zip(parsed_results, log_paths):
            run_figs = generate_training_curve(
                parsed.get("metrics_series", []),
                output_dir=self.figures_dir,
                run_name=parsed.get("source_file") or log_path.stem,
            )
            figures.extend(run_figs)

        first = parsed_results[0]
        summary = summarize_metrics(first)

        report_path = None
        if make_report:
            used_tools.append("generate_markdown_report")
            report_path = generate_markdown_report(
                parsed_log=first,
                metrics_summary=summary,
                figures=figures,
                citations=citations,
                output_dir=self.reports_dir,
                title="Plant3D Training Log Analysis Report",
            )

        answer_parts = [
            "### 训练日志分析结果",
            summary["summary"],
            "",
            "### 可能问题",
            *[f"- {item}" for item in summary.get("diagnosis", [])],
            "",
            "### 下一步建议",
            *[f"- {item}" for item in summary.get("suggestions", [])],
        ]

        if len(parsed_results) > 1:
            used_tools.append("compare_models")
            comparison = compare_models(parsed_results)
            answer_parts.extend(["", "### 多日志对比", comparison["summary"]])
            for row in comparison["ranking"]:
                answer_parts.append(
                    f"- {row['experiment']}: best mIoU={_fmt(row.get('best_miou'))}, best F1={_fmt(row.get('best_f1'))}"
                )

        if first.get("warnings"):
            answer_parts.extend(["", "### Parser Warnings", *[f"- {item}" for item in first["warnings"]]])

        return {
            "answer": "\n".join(answer_parts),
            "used_tools": used_tools,
            "citations": citations,
            "figures": figures,
            "report_path": report_path,
            "metrics": summary,
            "parsed_log": first,
        }

    def _run_model_compare(self, query: str, paths: list[Path]) -> dict[str, Any]:
        used_tools: list[str] = []
        log_paths = self._candidate_log_paths(paths)
        csv_paths = [path for path in paths if path.suffix.lower() == ".csv" and path.exists()]
        citations = self._retrieve_citations(query)

        if log_paths:
            used_tools.extend(["parse_training_log", "compare_models"])
            parsed = [parse_training_log(path) for path in log_paths]
            comparison = compare_models(parsed)
            lines = ["### 模型/实验对比", comparison["summary"]]
            for row in comparison["ranking"]:
                lines.append(
                    f"- {row['experiment']}: best mIoU={_fmt(row.get('best_miou'))}, best F1={_fmt(row.get('best_f1'))}"
                )
            return {
                "answer": "\n".join(lines),
                "used_tools": used_tools,
                "citations": citations,
                "figures": [],
                "report_path": None,
                "comparison": comparison,
            }

        if csv_paths:
            used_tools.append("compare_models")
            answer = self._compare_metrics_csv(csv_paths[0])
            return {
                "answer": answer,
                "used_tools": used_tools,
                "citations": citations,
                "figures": [],
                "report_path": None,
            }

        return self._run_doc_qa(query)

    def _compare_metrics_csv(self, csv_path: Path) -> str:
        try:
            frame = pd.read_csv(csv_path)
        except Exception as exc:
            return f"无法读取实验表格 {csv_path.name}: {exc}"
        if frame.empty:
            return f"实验表格 {csv_path.name} 为空。"

        metric_columns = [col for col in frame.columns if col.lower() in {"miou", "f1", "oa", "precision", "recall"}]
        model_col = next((col for col in frame.columns if col.lower() in {"model", "method", "experiment"}), frame.columns[0])
        sort_col = "mIoU" if "mIoU" in frame.columns else ("miou" if "miou" in frame.columns else metric_columns[0] if metric_columns else None)
        if sort_col:
            ranked = frame.sort_values(sort_col, ascending=False)
        else:
            ranked = frame

        lines = [f"### 实验表格对比：{csv_path.name}"]
        if sort_col:
            lines.append(f"按 {sort_col} 从高到低排序：")
        for _, row in ranked.head(10).iterrows():
            metrics = ", ".join(f"{col}={row[col]}" for col in metric_columns if col in row)
            lines.append(f"- {row[model_col]}: {metrics}")
        return "\n".join(lines)

    def _run_doc_qa(self, query: str) -> dict[str, Any]:
        used_tools = ["rag_retrieve_context"]
        citations = self._retrieve_citations(query)
        if not citations:
            return {
                "answer": "当前知识库没有检索到相关片段。请先上传论文笔记、实验表格或日志，然后点击构建知识库。",
                "used_tools": used_tools,
                "citations": [],
                "figures": [],
                "report_path": None,
            }

        answer = self._compose_rag_answer(query, citations)
        return {
            "answer": answer,
            "used_tools": used_tools,
            "citations": citations,
            "figures": [],
            "report_path": None,
        }

    def _run_general_advice(self, query: str) -> dict[str, Any]:
        citations = self._retrieve_citations(query)
        context = "\n\n".join(f"[{item['source']}]\n{item['chunk']}" for item in citations)
        prompt = (
            "User question:\n"
            f"{query}\n\n"
            "Retrieved context:\n"
            f"{context or 'No retrieved context.'}\n\n"
            "Answer in concise research-oriented Chinese for 3D plant point cloud segmentation."
        )
        answer = self.llm.generate(prompt)
        return {
            "answer": answer,
            "used_tools": ["rag_retrieve_context"] if citations else [],
            "citations": citations,
            "figures": [],
            "report_path": None,
        }

    def _retrieve_citations(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        try:
            raw = rag_retrieve_context(query, top_k=top_k)
        except Exception:
            return []
        citations: list[dict[str, Any]] = []
        for item in raw:
            chunk = str(item.get("chunk") or item.get("text") or "")
            if not chunk.strip():
                continue
            citations.append(
                {
                    "source": item.get("source", "unknown"),
                    "chunk": chunk,
                    "score": item.get("score", 0.0),
                }
            )
        return citations

    def _compose_rag_answer(self, query: str, citations: list[dict[str, Any]]) -> str:
        context = "\n\n".join(f"[{item['source']}]\n{item['chunk']}" for item in citations)
        if self.llm.provider_name != "mock":
            prompt = (
                f"Question: {query}\n\n"
                f"Context:\n{context}\n\n"
                "Use only the retrieved context when possible. Include concise reasoning and cite source filenames."
            )
            return self.llm.generate(prompt)

        lower_context = context.lower()
        if "plant-geoat" in lower_context and "boundary" in lower_context:
            reason = (
                "基于检索到的笔记，Plant-GeoAT 缓解 leaf-stem boundary confusion 的核心原因是："
                "它把局部几何关系、邻域拓扑和边界附近的方向/曲率线索显式纳入特征聚合，"
                "使模型在叶片和茎秆交界处不只依赖点坐标或颜色强度，而能利用细长结构、法向变化和局部连接关系来区分类别。"
                "这通常会提升 stem IoU，并减少薄茎被叶片吞并的错误。"
            )
        else:
            reason = (
                "基于当前检索片段，答案主要来自相关文档中的实验描述和指标解释。"
                "建议结合 class-wise IoU、边界区域可视化和失败案例截图进一步验证。"
            )
        sources = ", ".join(sorted({item["source"] for item in citations}))
        return f"{reason}\n\n来源：{sources}"


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
