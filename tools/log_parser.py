"""Training log parsing utilities for 3D plant point cloud experiments."""

from __future__ import annotations

import re
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


Number = float | int


METRIC_ALIASES: dict[str, list[str]] = {
    "train_loss": [
        r"train[_\s/-]*loss",
        r"loss[_\s/-]*train",
        r"training[_\s/-]*loss",
    ],
    "val_loss": [
        r"val(?:idation)?[_\s/-]*loss",
        r"loss[_\s/-]*val",
    ],
    "miou": [
        r"mIoU",
        r"mean[_\s-]*IoU",
        r"val[_\s/-]*mIoU",
    ],
    "macc": [
        r"mAcc",
        r"mean[_\s-]*Acc(?:uracy)?",
    ],
    "oa": [
        r"OA",
        r"overall[_\s-]*acc(?:uracy)?",
        r"overall[_\s-]*accuracy",
    ],
    "precision": [r"precision", r"prec"],
    "recall": [r"recall"],
    "f1": [r"F1(?:[_\s-]*score)?", r"f1_score"],
    "leaf_iou": [
        r"leaf[_\s-]*IoU",
        r"IoU[_\s-]*leaf",
        r"class[_\s-]*leaf[_\s-]*IoU",
    ],
    "stem_iou": [
        r"stem[_\s-]*IoU",
        r"IoU[_\s-]*stem",
        r"class[_\s-]*stem[_\s-]*IoU",
    ],
    "best_miou": [r"best[_\s-]*mIoU", r"best[_\s-]*mean[_\s-]*IoU"],
    "best_f1": [r"best[_\s-]*F1(?:[_\s-]*score)?", r"best_f1"],
}

FLOAT_PATTERN = r"([-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?)\s*%?"


def _read_text(path_or_text: str | Path) -> tuple[str, str | None]:
    path = Path(path_or_text)
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore"), path.name
    return str(path_or_text), None


def _normalize_metric_value(key: str, value: float, raw_token: str) -> float:
    """Normalize percentage-like metric values to the 0-1 range."""
    if "loss" in key:
        return value
    if "%" in raw_token or 1.5 < abs(value) <= 100:
        return value / 100.0
    return value


def _extract_metric(line: str, key: str) -> float | None:
    for alias in METRIC_ALIASES[key]:
        patterns = [
            rf"\b(?:{alias})\b\s*(?:[:=]|is|=)?\s*{FLOAT_PATTERN}",
            rf"\b(?:{alias})\b\s+{FLOAT_PATTERN}",
        ]
        for pattern in patterns:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if match:
                raw = match.group(1)
                try:
                    return _normalize_metric_value(key, float(raw), match.group(0))
                except ValueError:
                    return None
    return None


def _extract_epoch(line: str) -> int | None:
    patterns = [
        r"\bepoch\b\s*(?:\[|\()?[:=]?\s*(\d+)(?:\s*/\s*\d+)?",
        r"\bep\b\s*[:=]?\s*(\d+)\b",
        r"\[(\d+)\s*/\s*\d+\]",
    ]
    for pattern in patterns:
        match = re.search(pattern, line, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _extract_best_metric(line: str, metric_name: str) -> tuple[float | None, int | None]:
    """Extract best metric value and optional epoch from a log line."""
    aliases = METRIC_ALIASES[metric_name]
    for alias in aliases:
        value_match = re.search(
            rf"\b(?:{alias})\b\s*(?:[:=]|is|at)?\s*{FLOAT_PATTERN}",
            line,
            flags=re.IGNORECASE,
        )
        if not value_match:
            continue
        raw = value_match.group(1)
        try:
            value = _normalize_metric_value(metric_name, float(raw), value_match.group(0))
        except ValueError:
            value = None
        epoch = None
        epoch_match = re.search(
            r"\b(?:epoch|ep)\b\s*(?:[:=]|at)?\s*(\d+)",
            line,
            flags=re.IGNORECASE,
        )
        if epoch_match:
            try:
                epoch = int(epoch_match.group(1))
            except ValueError:
                epoch = None
        return value, epoch
    return None, None


def _best_from_series(series: list[dict[str, Any]], key: str) -> tuple[float | None, int | None]:
    available = [
        (row.get(key), row.get("epoch"))
        for row in series
        if isinstance(row.get(key), (int, float))
    ]
    if not available:
        return None, None
    best_value, best_epoch = max(available, key=lambda item: float(item[0]))
    return float(best_value), int(best_epoch) if best_epoch is not None else None


def _series_values(series: list[dict[str, Any]], key: str) -> list[float]:
    return [float(row[key]) for row in series if isinstance(row.get(key), (int, float))]


def _build_warnings(series: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    f1_values = _series_values(series, "f1")
    if len(f1_values) >= 6:
        recent = f1_values[-max(5, min(10, len(f1_values))) :]
        if pstdev(recent) > 0.025:
            warnings.append("F1 fluctuates strongly in recent epochs")

    leaf_values = _series_values(series, "leaf_iou")
    stem_values = _series_values(series, "stem_iou")
    if leaf_values and stem_values:
        diff = mean(leaf_values) - mean(stem_values)
        if diff > 0.08:
            warnings.append("Stem IoU is consistently lower than Leaf IoU")

    miou_values = _series_values(series, "miou")
    if len(miou_values) >= 8:
        best_index = max(range(len(miou_values)), key=lambda idx: miou_values[idx])
        final_drop = miou_values[best_index] - miou_values[-1]
        if best_index < len(miou_values) * 0.7 and final_drop > 0.03:
            warnings.append("Validation mIoU drops after the best epoch; possible overfitting")
    return warnings


def parse_training_log(path_or_text: str | Path) -> dict[str, Any]:
    """Parse a training log into metric series and best metric metadata.

    The parser intentionally uses forgiving regular expressions because research
    logs often differ between projects and training scripts.
    """
    text, source_name = _read_text(path_or_text)
    metrics_series: list[dict[str, Any]] = []
    explicit_best_miou: float | None = None
    explicit_best_miou_epoch: int | None = None
    explicit_best_f1: float | None = None
    explicit_best_f1_epoch: int | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lowered = line.lower()
        if "best" in lowered:
            best_miou, best_miou_epoch = _extract_best_metric(line, "best_miou")
            best_f1, best_f1_epoch = _extract_best_metric(line, "best_f1")
            if best_miou is not None:
                explicit_best_miou = best_miou
                explicit_best_miou_epoch = best_miou_epoch or explicit_best_miou_epoch
            if best_f1 is not None:
                explicit_best_f1 = best_f1
                explicit_best_f1_epoch = best_f1_epoch or explicit_best_f1_epoch
            if not re.search(r"\bepoch\b.*\b(train|val|loss|miou|f1)\b", lowered):
                continue

        epoch = _extract_epoch(line)
        row: dict[str, Number | None] = {"epoch": epoch}
        for key in [
            "train_loss",
            "val_loss",
            "miou",
            "macc",
            "oa",
            "precision",
            "recall",
            "f1",
            "leaf_iou",
            "stem_iou",
        ]:
            value = _extract_metric(line, key)
            if value is not None:
                row[key] = value

        metric_count = len([key for key in row if key != "epoch" and row[key] is not None])
        if epoch is not None and metric_count > 0:
            metrics_series.append(row)

    inferred_best_miou, inferred_best_miou_epoch = _best_from_series(metrics_series, "miou")
    inferred_best_f1, inferred_best_f1_epoch = _best_from_series(metrics_series, "f1")

    best_miou = explicit_best_miou if explicit_best_miou is not None else inferred_best_miou
    best_f1 = explicit_best_f1 if explicit_best_f1 is not None else inferred_best_f1
    best_miou_epoch = explicit_best_miou_epoch or inferred_best_miou_epoch
    best_f1_epoch = explicit_best_f1_epoch or inferred_best_f1_epoch

    epochs = [row.get("epoch") for row in metrics_series if row.get("epoch") is not None]
    return {
        "source_file": source_name,
        "num_epochs": len(set(epochs)) if epochs else len(metrics_series),
        "best_miou": best_miou,
        "best_miou_epoch": best_miou_epoch,
        "best_f1": best_f1,
        "best_f1_epoch": best_f1_epoch,
        "metrics_series": metrics_series,
        "warnings": _build_warnings(metrics_series),
    }
