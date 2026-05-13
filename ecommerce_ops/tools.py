"""Tool functions wrapping e-commerce ops analysis capabilities."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ecommerce_ops.analyzers import (
    analyze_campaign_performance,
    analyze_product_anomalies,
    analyze_task_followup,
    generate_next_actions,
    generate_ops_suggestions,
)
from ecommerce_ops.data_loader import load_all
from ecommerce_ops.schemas import CampaignInsight, ProductAnomaly, TaskItem


def _preview(df: pd.DataFrame, n: int = 10) -> list[dict[str, Any]]:
    """Return first N rows of a DataFrame as dicts for JSON preview."""
    return df.head(n).fillna("").to_dict(orient="records")


def check_product_anomalies(
    products_path: str | None = None,
) -> tuple[list[ProductAnomaly], list[dict[str, Any]]]:
    """Check products for stock, conversion, refund, and rating anomalies.

    Returns:
        (list of ProductAnomaly, data preview dicts)
    """
    df, _, _ = load_all() if products_path is None else (_load_products_df(products_path), pd.DataFrame(), pd.DataFrame())
    anomalies = analyze_product_anomalies(df)
    return anomalies, _preview(df)


def _load_products_df(path: str) -> pd.DataFrame:
    from ecommerce_ops.data_loader import load_products
    return load_products(path)


def review_campaign_performance(
    campaigns_path: str | None = None,
) -> tuple[list[CampaignInsight], list[dict[str, Any]]]:
    """Review campaign ROI, CTR, and spend efficiency.

    Returns:
        (list of CampaignInsight, data preview dicts)
    """
    _, df, _ = load_all() if campaigns_path is None else (pd.DataFrame(), _load_campaigns_df(campaigns_path), pd.DataFrame())
    insights = analyze_campaign_performance(df)
    return insights, _preview(df)


def _load_campaigns_df(path: str) -> pd.DataFrame:
    from ecommerce_ops.data_loader import load_campaigns
    return load_campaigns(path)


def list_pending_tasks(
    tasks_path: str | None = None,
) -> tuple[list[TaskItem], list[dict[str, Any]]]:
    """List pending and overdue tasks sorted by urgency.

    Returns:
        (list of TaskItem, data preview dicts)
    """
    _, _, df = load_all() if tasks_path is None else (pd.DataFrame(), pd.DataFrame(), _load_tasks_df(tasks_path))
    tasks = analyze_task_followup(df)
    return tasks, _preview(df)


def _load_tasks_df(path: str) -> pd.DataFrame:
    from ecommerce_ops.data_loader import load_tasks
    return load_tasks(path)


def generate_ops_report(
    report_type: str = "daily",
    products_path: str | None = None,
    campaigns_path: str | None = None,
    tasks_path: str | None = None,
) -> dict[str, Any]:
    """Generate a structured ops report with anomalies, insights, tasks, and actions.

    Returns:
        dict with keys: report_type, product_anomalies, campaign_insights,
                        pending_tasks, suggestions, next_actions, data_preview
    """
    prods, camps, tasks_df = load_all()

    anomalies = analyze_product_anomalies(prods)
    insights = analyze_campaign_performance(camps)
    pending = analyze_task_followup(tasks_df)
    suggestions = generate_ops_suggestions(anomalies, insights, pending)
    next_actions = generate_next_actions(anomalies, insights, pending)

    return {
        "report_type": report_type,
        "product_anomalies": anomalies,
        "campaign_insights": insights,
        "pending_tasks": pending,
        "suggestions": suggestions,
        "next_actions": next_actions,
        "data_preview": {
            "products": _preview(prods, 5),
            "campaigns": _preview(camps, 5),
            "tasks": _preview(tasks_df, 5),
        },
    }


def generate_merchant_message(
    anomalies: list[ProductAnomaly] | None = None,
    tasks: list[TaskItem] | None = None,
) -> str:
    """Generate a merchant-facing reminder message based on anomalies and tasks.

    Returns:
        Formatted markdown string suitable for merchant notification.
    """
    parts: list[str] = ["## 商家运营提醒\n"]

    anomalies = anomalies or []
    tasks = tasks or []

    if tasks:
        urgent = [t for t in tasks if t.urgency in ("critical", "high")]
        if urgent:
            parts.append("### 紧急待办")
            for t in urgent[:5]:
                parts.append(f"- **{t.task_id}** [{t.priority}] {t.description}（截止 {t.deadline}）")

    if anomalies:
        stock = [a for a in anomalies if a.anomaly_type == "low_stock"]
        if stock:
            parts.append("\n### 补货提醒")
            for a in stock[:5]:
                parts.append(f"- {a.product_id} {a.title}: {a.reason}")

        quality = [a for a in anomalies if a.anomaly_type in ("high_refund_rate", "low_rating")]
        if quality:
            parts.append("\n### 商品质量关注")
            for a in quality[:5]:
                parts.append(f"- {a.product_id} {a.title}: {a.reason} → {a.suggestion}")

    if len(parts) == 1:
        parts.append("\n当前无紧急运营事项，各项指标正常。")

    parts.append(f"\n> 本提醒由 E-commerce Ops Agent 自动生成，数据基于近30天运营数据。")
    return "\n".join(parts)
