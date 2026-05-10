"""Rule-based metric analysis for Plant3D segmentation experiments."""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any


def _values(series: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in series if isinstance(row.get(key), (int, float))]


def _final_epoch(series: list[dict[str, Any]]) -> int | None:
    epochs = [int(row["epoch"]) for row in series if isinstance(row.get("epoch"), int)]
    return max(epochs) if epochs else None


def _format_metric(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.4f}"


def summarize_metrics(parsed_log: dict[str, Any]) -> dict[str, Any]:
    """Summarize parsed log metrics and produce rule-based diagnosis."""
    series = parsed_log.get("metrics_series", []) or []
    best_miou = parsed_log.get("best_miou")
    best_f1 = parsed_log.get("best_f1")
    best_miou_epoch = parsed_log.get("best_miou_epoch")
    best_f1_epoch = parsed_log.get("best_f1_epoch")
    final_epoch = _final_epoch(series)

    diagnosis: list[str] = []
    suggestions: list[str] = []

    miou_values = _values(series, "miou")
    f1_values = _values(series, "f1")
    leaf_iou_values = _values(series, "leaf_iou")
    stem_iou_values = _values(series, "stem_iou")

    if final_epoch and best_miou_epoch and miou_values and isinstance(best_miou, (int, float)):
        final_miou = miou_values[-1]
        if best_miou_epoch < final_epoch * 0.7 and final_miou < float(best_miou) - 0.03:
            diagnosis.append(
                "Best mIoU appears much earlier than the final epoch and later validation performance declines, suggesting possible overfitting."
            )
            suggestions.append(
                "Try early stopping, stronger weight decay, data augmentation, or a lower learning rate after the plateau."
            )

    recent_metric = f1_values[-10:] if len(f1_values) >= 10 else miou_values[-10:]
    if len(recent_metric) >= 5 and pstdev(recent_metric) > 0.025:
        diagnosis.append("Recent validation metrics fluctuate noticeably, indicating unstable training or validation noise.")
        suggestions.append(
            "Check batch size, learning-rate schedule, random seed sensitivity, and whether validation scenes are too heterogeneous."
        )

    if leaf_iou_values and stem_iou_values:
        leaf_mean = mean(leaf_iou_values)
        stem_mean = mean(stem_iou_values)
        gap = leaf_mean - stem_mean
        if gap > 0.08:
            diagnosis.append(
                f"Stem IoU is lower than leaf IoU by about {gap:.3f}, which points to thin-structure errors or class imbalance."
            )
            suggestions.append(
                "Consider class-balanced sampling/losses, boundary-aware augmentation, and geometry features that preserve thin stems."
            )

    if isinstance(best_f1, (int, float)) and isinstance(best_miou, (int, float)):
        gap = abs(float(best_f1) - float(best_miou))
        if gap > 0.12:
            diagnosis.append(
                "The gap between F1 and mIoU is large, so instance boundaries or minority-class predictions may be unstable."
            )
            suggestions.append(
                "Inspect class-wise IoU and boundary confusion matrices, especially leaf-stem transitions and occluded organs."
            )

    if not diagnosis:
        diagnosis.append("No severe rule-based warning was detected from the available metrics.")
    if not suggestions:
        suggestions.append("Run an ablation over learning rate, augmentation strength, and class-balanced loss to validate robustness.")

    summary = (
        f"Parsed {parsed_log.get('num_epochs', len(series))} epochs. "
        f"Best mIoU={_format_metric(best_miou)}"
        f"{f' at epoch {best_miou_epoch}' if best_miou_epoch else ''}; "
        f"Best F1={_format_metric(best_f1)}"
        f"{f' at epoch {best_f1_epoch}' if best_f1_epoch else ''}. "
        f"Final epoch={final_epoch or 'N/A'}."
    )

    return {
        "summary": summary,
        "key_metrics": {
            "best_miou": best_miou,
            "best_miou_epoch": best_miou_epoch,
            "best_f1": best_f1,
            "best_f1_epoch": best_f1_epoch,
            "final_epoch": final_epoch,
            "leaf_iou_mean": mean(leaf_iou_values) if leaf_iou_values else None,
            "stem_iou_mean": mean(stem_iou_values) if stem_iou_values else None,
        },
        "diagnosis": diagnosis,
        "suggestions": suggestions,
    }


def compare_models(parsed_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare multiple parsed experiment logs by best mIoU and F1."""
    rows: list[dict[str, Any]] = []
    for index, parsed in enumerate(parsed_results, start=1):
        source = parsed.get("source_file") or f"experiment_{index}"
        rows.append(
            {
                "experiment": source,
                "best_miou": parsed.get("best_miou"),
                "best_f1": parsed.get("best_f1"),
                "best_miou_epoch": parsed.get("best_miou_epoch"),
                "best_f1_epoch": parsed.get("best_f1_epoch"),
            }
        )

    def score(row: dict[str, Any]) -> float:
        miou = row.get("best_miou")
        f1 = row.get("best_f1")
        return float(miou if miou is not None else 0.0) + 0.5 * float(f1 if f1 is not None else 0.0)

    ranked = sorted(rows, key=score, reverse=True)
    winner = ranked[0]["experiment"] if ranked else None
    return {
        "ranking": ranked,
        "summary": f"Best overall experiment: {winner}" if winner else "No comparable experiments were found.",
    }
