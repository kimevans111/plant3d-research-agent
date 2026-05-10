"""Matplotlib plotting helpers for training curves."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _safe_slug(value: str | None) -> str:
    if not value:
        return "experiment"
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()
    return slug or "experiment"


def _series_xy(metrics_series: list[dict[str, Any]], key: str) -> tuple[list[int], list[float]]:
    xs: list[int] = []
    ys: list[float] = []
    for index, row in enumerate(metrics_series, start=1):
        value = row.get(key)
        if isinstance(value, (int, float)):
            xs.append(int(row.get("epoch") or index))
            ys.append(float(value))
    return xs, ys


def _save_single_curve(
    x: list[int],
    y: list[float],
    title: str,
    ylabel: str,
    output_path: Path,
) -> str:
    plt.figure(figsize=(8, 4.8))
    plt.plot(x, y, marker="o", linewidth=1.6, markersize=3)
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def _save_loss_curve(metrics_series: list[dict[str, Any]], output_path: Path) -> str | None:
    train_x, train_y = _series_xy(metrics_series, "train_loss")
    val_x, val_y = _series_xy(metrics_series, "val_loss")
    if not train_y and not val_y:
        return None

    plt.figure(figsize=(8, 4.8))
    if train_y:
        plt.plot(train_x, train_y, marker="o", linewidth=1.6, markersize=3, label="train loss")
    if val_y:
        plt.plot(val_x, val_y, marker="s", linewidth=1.6, markersize=3, label="val loss")
    plt.title("Loss vs Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def generate_training_curve(
    metrics_series: list[dict[str, Any]],
    output_dir: str | Path = "reports/figures",
    run_name: str | None = None,
) -> list[str]:
    """Generate mIoU, F1, and loss curves when the relevant metrics exist."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(run_name)
    figures: list[str] = []

    miou_x, miou_y = _series_xy(metrics_series, "miou")
    if miou_y:
        figures.append(
            _save_single_curve(
                miou_x,
                miou_y,
                "mIoU vs Epoch",
                "mIoU",
                output / f"{slug}_miou_curve.png",
            )
        )

    f1_x, f1_y = _series_xy(metrics_series, "f1")
    if f1_y:
        figures.append(
            _save_single_curve(
                f1_x,
                f1_y,
                "F1 vs Epoch",
                "F1-score",
                output / f"{slug}_f1_curve.png",
            )
        )

    loss_figure = _save_loss_curve(metrics_series, output / f"{slug}_loss_curve.png")
    if loss_figure:
        figures.append(loss_figure)

    return figures
