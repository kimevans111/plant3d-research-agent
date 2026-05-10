"""Markdown report generation for Plant3D experiments."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


def _slugify(value: str | None) -> str:
    if not value:
        return "experiment"
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()
    return slug or "experiment"


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def generate_markdown_report(
    parsed_log: dict[str, Any] | None = None,
    metrics_summary: dict[str, Any] | None = None,
    figures: list[str] | None = None,
    citations: list[dict[str, Any]] | None = None,
    output_dir: str | Path = "reports",
    report_name: str | None = None,
    title: str = "Plant3D Experiment Analysis Report",
    answer: str | None = None,
) -> str:
    """Generate a Markdown report and return the saved path."""
    parsed_log = parsed_log or {}
    metrics_summary = metrics_summary or {}
    figures = figures or []
    citations = citations or []

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    source = parsed_log.get("source_file") or report_name or "experiment"
    filename = f"report_{_slugify(str(source))}.md"
    path = output / filename

    key_metrics = metrics_summary.get("key_metrics", {})
    lines = [
        f"# {title}",
        "",
        f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Source file: {_fmt(parsed_log.get('source_file'))}",
        "",
        "## Experiment Overview",
        "",
        metrics_summary.get("summary", "No summary is available."),
        "",
        "## Key Metrics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Best mIoU | {_fmt(key_metrics.get('best_miou', parsed_log.get('best_miou')))} |",
        f"| Best mIoU Epoch | {_fmt(key_metrics.get('best_miou_epoch', parsed_log.get('best_miou_epoch')))} |",
        f"| Best F1 | {_fmt(key_metrics.get('best_f1', parsed_log.get('best_f1')))} |",
        f"| Best F1 Epoch | {_fmt(key_metrics.get('best_f1_epoch', parsed_log.get('best_f1_epoch')))} |",
        f"| Final Epoch | {_fmt(key_metrics.get('final_epoch'))} |",
        f"| Mean Leaf IoU | {_fmt(key_metrics.get('leaf_iou_mean'))} |",
        f"| Mean Stem IoU | {_fmt(key_metrics.get('stem_iou_mean'))} |",
        "",
        "## Training Process Analysis",
        "",
    ]

    diagnosis = metrics_summary.get("diagnosis", [])
    if diagnosis:
        lines.extend([f"- {item}" for item in diagnosis])
    else:
        lines.append("- No diagnosis was generated.")

    lines.extend(["", "## Next-Step Suggestions", ""])
    suggestions = metrics_summary.get("suggestions", [])
    if suggestions:
        lines.extend([f"- {item}" for item in suggestions])
    else:
        lines.append("- No suggestions were generated.")

    if answer:
        lines.extend(["", "## Agent Answer", "", answer])

    lines.extend(["", "## Generated Curves", ""])
    if figures:
        for figure in figures:
            figure_path = Path(figure)
            lines.append(f"- {figure_path.name}: `{figure}`")
    else:
        lines.append("- No curve was generated because no plottable metric series was found.")

    lines.extend(["", "## RAG Citations", ""])
    if citations:
        for citation in citations:
            source_name = citation.get("source", "unknown")
            chunk = str(citation.get("chunk") or citation.get("text") or "").replace("\n", " ")
            lines.append(f"- **{source_name}**: {chunk[:500]}")
    else:
        lines.append("- No external context was cited.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)
