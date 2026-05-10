"""Markdown report generation for RAG-Eval Mini."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


METRIC_NAMES = [
    "source_hit_at_k",
    "keyword_recall",
    "citation_hit",
    "answer_point_coverage",
    "retrieval_empty_rate",
    "average_score",
]


def generate_markdown_report(
    result: dict[str, Any],
    output_dir: str | Path,
    retriever_type: str,
    top_k: int,
    use_agent_answer: bool,
    mock_provider: bool,
    timestamp: str | None = None,
) -> Path:
    """Write a RAG evaluation report and return its path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"rag_eval_report_{stamp}.md"
    path.write_text(
        build_markdown_report(
            result=result,
            retriever_type=retriever_type,
            top_k=top_k,
            use_agent_answer=use_agent_answer,
            mock_provider=mock_provider,
        ),
        encoding="utf-8",
    )
    return path


def build_markdown_report(
    result: dict[str, Any],
    retriever_type: str,
    top_k: int,
    use_agent_answer: bool,
    mock_provider: bool,
) -> str:
    """Build a Markdown report string from evaluation results."""
    summary = result["summary"]
    items = result["items"]
    lines: list[str] = [
        "# RAG Evaluation Report",
        "",
        "## 1. Overview",
        "",
        f"- Number of questions: {summary.get('num_questions', 0)}",
        f"- Retriever type: {retriever_type}",
        f"- top_k: {top_k}",
        f"- LLM answer generation enabled: {use_agent_answer}",
        f"- Mock provider used: {mock_provider}",
        "",
        "## 2. Summary Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for metric in METRIC_NAMES:
        if metric in summary:
            lines.append(f"| `{metric}` | {summary[metric]:.4f} |")

    lines.extend(["", "## 3. Metrics by Category", "", "| Category | Questions | Average Score | Source Hit | Keyword Recall | Citation Hit | Answer Coverage |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for category, stats in sorted(_category_stats(items).items()):
        lines.append(
            "| {category} | {count} | {average_score:.4f} | {source_hit_at_k:.4f} | {keyword_recall:.4f} | {citation_hit:.4f} | {answer_point_coverage:.4f} |".format(
                category=category,
                **stats,
            )
        )

    lines.extend(["", "## 4. Failure Cases", ""])
    failures = [item for item in items if item.get("average_score", 0.0) < 0.65 or item.get("failure_reason")]
    if not failures:
        lines.append("No major failure cases were found under the current threshold.")
    for item in sorted(failures, key=lambda row: row.get("average_score", 0.0))[:10]:
        lines.extend(
            [
                f"### {item['id']} - {item['question']}",
                "",
                f"- Expected sources: {', '.join(item.get('expected_sources', [])) or 'N/A'}",
                f"- Retrieved sources: {', '.join(item.get('retrieved_sources', [])) or 'N/A'}",
                f"- Missing keywords: {', '.join(item.get('missing_keywords', [])) or 'None'}",
                f"- Possible reason: {item.get('failure_reason') or 'Low combined metric score.'}",
                f"- Suggested fix: {_suggest_fix(item)}",
                "",
            ]
        )

    lines.extend(["## 5. Optimization Suggestions", ""])
    lines.extend(f"- {item}" for item in _optimization_suggestions(summary))

    lines.extend(["", "## 6. Detailed Results", ""])
    for item in items:
        lines.extend(
            [
                f"### {item['id']} | {item['category']} | score={item['average_score']:.4f}",
                "",
                f"Question: {item['question']}",
                "",
                f"- source_hit_at_k: {item['source_hit_at_k']:.4f}",
                f"- keyword_recall: {item['keyword_recall']:.4f}",
                f"- citation_hit: {item['citation_hit']:.4f}",
                f"- answer_point_coverage: {item['answer_point_coverage']:.4f}",
                f"- retrieved_sources: {', '.join(item.get('retrieved_sources', [])) or 'N/A'}",
                "",
            ]
        )
        previews = item.get("retrieved_preview", [])
        if previews:
            lines.append("Retrieved preview:")
            lines.append("")
            for preview in previews[:2]:
                lines.append(f"> {_one_line(preview)[:350]}")
            lines.append("")
    return "\n".join(lines)


def _category_stats(items: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item.get("category", "unknown")].append(item)
    stats: dict[str, dict[str, float | int]] = {}
    for category, rows in grouped.items():
        count = len(rows)
        stats[category] = {
            "count": count,
            "average_score": _avg(rows, "average_score"),
            "source_hit_at_k": _avg(rows, "source_hit_at_k"),
            "keyword_recall": _avg(rows, "keyword_recall"),
            "citation_hit": _avg(rows, "citation_hit"),
            "answer_point_coverage": _avg(rows, "answer_point_coverage"),
        }
    return stats


def _avg(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row.get(key, 0.0)) for row in rows]
    return sum(values) / len(values) if values else 0.0


def _suggest_fix(item: dict[str, Any]) -> str:
    if item.get("source_hit_at_k", 0) < 1:
        return "Check chunk splitting, source metadata, and top_k."
    if item.get("keyword_recall", 0.0) < 0.5:
        return "Improve query rewrite, hybrid search, or embedding quality."
    if item.get("citation_hit", 0) < 1:
        return "Check citation binding from retrieved chunks to source filenames."
    if item.get("answer_point_coverage", 0.0) < 0.5:
        return "Improve answer prompt or pass more relevant context."
    return "Inspect retrieved chunks and expected labels for mismatch."


def _optimization_suggestions(summary: dict[str, Any]) -> list[str]:
    suggestions: list[str] = []
    if summary.get("source_hit_at_k", 0.0) < 0.75:
        suggestions.append("If source_hit_at_k is low, inspect chunk boundaries, source metadata, and top_k.")
    if summary.get("keyword_recall", 0.0) < 0.65:
        suggestions.append("If keyword_recall is low, add query rewrite, stronger embeddings, or hybrid keyword search.")
    if summary.get("citation_hit", 0.0) < 0.75:
        suggestions.append("If citation_hit is low, verify that answer citations are bound to retrieved chunk metadata.")
    if summary.get("answer_point_coverage", 0.0) < 0.6:
        suggestions.append("If answer_point_coverage is low, improve the answer prompt or increase relevant context.")
    if summary.get("retrieval_empty_rate", 0.0) > 0.05:
        suggestions.append("If retrieval_empty_rate is high, check index building, document loading, and supported file types.")
    if not suggestions:
        suggestions.append("Current scores are healthy for a lightweight MVP; expand the eval set before tuning further.")
    return suggestions


def _one_line(value: str) -> str:
    return " ".join(value.split())
