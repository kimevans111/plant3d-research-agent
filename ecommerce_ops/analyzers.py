"""Analysis functions for products, campaigns, and tasks."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from ecommerce_ops.schemas import CampaignInsight, ProductAnomaly, TaskItem


def analyze_product_anomalies(df: pd.DataFrame) -> list[ProductAnomaly]:
    """Detect product anomalies: low stock, low conversion, high refund, low rating."""
    anomalies: list[ProductAnomaly] = []

    for _, row in df.iterrows():
        pid = str(row["product_id"])
        title = str(row["title"])
        cat = str(row["category"])

        stock = float(row["stock"])
        if stock < 100:
            anomalies.append(
                ProductAnomaly(
                    product_id=pid,
                    title=title,
                    category=cat,
                    anomaly_type="low_stock",
                    current_value=stock,
                    threshold=100,
                    reason=f"库存仅剩 {int(stock)} 件，低于安全库存线 100 件",
                    suggestion="建议立即补货，避免断货影响销售和搜索权重",
                )
            )

        conv = float(row["conversion_rate"])
        impressions = float(row["impressions"])
        if conv < 0.013 and impressions > 30000:
            anomalies.append(
                ProductAnomaly(
                    product_id=pid,
                    title=title,
                    category=cat,
                    anomaly_type="low_conversion_high_exposure",
                    current_value=conv,
                    threshold=0.013,
                    reason=f"转化率 {conv:.3f} 低于阈值 0.013，但曝光量高达 {int(impressions)}",
                    suggestion="建议优化商品主图、详情页或价格策略，提升流量转化效率",
                )
            )

        refund = float(row["refund_rate"])
        if refund > 0.025:
            anomalies.append(
                ProductAnomaly(
                    product_id=pid,
                    title=title,
                    category=cat,
                    anomaly_type="high_refund_rate",
                    current_value=refund,
                    threshold=0.025,
                    reason=f"退款率 {refund:.3f} 超过阈值 0.025",
                    suggestion="建议检查商品质量、描述准确性和包装，减少因预期不符导致的退款",
                )
            )

        rating = float(row["rating"])
        if rating < 4.1:
            anomalies.append(
                ProductAnomaly(
                    product_id=pid,
                    title=title,
                    category=cat,
                    anomaly_type="low_rating",
                    current_value=rating,
                    threshold=4.1,
                    reason=f"评分 {rating:.1f} 低于 4.1，可能影响搜索推荐权重",
                    suggestion="建议分析差评原因，针对性改进商品或服务，并引导好评",
                )
            )

    return anomalies


def analyze_campaign_performance(df: pd.DataFrame) -> list[CampaignInsight]:
    """Analyze campaign performance: ROI, CTR, spend efficiency."""
    insights: list[CampaignInsight] = []

    for _, row in df.iterrows():
        cid = str(row["campaign_id"])
        name = str(row["campaign_name"])
        pid = str(row["product_id"])
        spend = float(row["spend"])
        orders = float(row["orders"])
        roi = float(row["roi"])
        impressions = float(row["impressions"])
        clicks = float(row["clicks"])
        status = str(row["status"])
        ctr = clicks / max(impressions, 1)

        if roi < 3.0:
            insights.append(
                CampaignInsight(
                    campaign_id=cid,
                    campaign_name=name,
                    product_id=pid,
                    spend=spend,
                    orders=int(orders),
                    roi=roi,
                    ctr=round(ctr, 4),
                    status=status,
                    insight=f"ROI 仅 {roi:.2f}，低于盈亏平衡线 3.0",
                    suggestion="建议暂停或缩减预算，分析人群定向和创意效果，或更换投放商品",
                )
            )

        if spend > 15000 and orders < 500:
            insights.append(
                CampaignInsight(
                    campaign_id=cid,
                    campaign_name=name,
                    product_id=pid,
                    spend=spend,
                    orders=int(orders),
                    roi=roi,
                    ctr=round(ctr, 4),
                    status=status,
                    insight=f"花费 {spend:.0f} 元但仅产生 {int(orders)} 单，投产效率低",
                    suggestion="建议检查投放关键词和人群精准度，考虑暂停或定向优化",
                )
            )

        if ctr < 0.01 and status == "active":
            insights.append(
                CampaignInsight(
                    campaign_id=cid,
                    campaign_name=name,
                    product_id=pid,
                    spend=spend,
                    orders=int(orders),
                    roi=roi,
                    ctr=round(ctr, 4),
                    status=status,
                    insight=f"CTR 仅 {ctr:.4f}，点击率偏低",
                    suggestion="建议优化创意素材和标题文案，测试不同视觉方案",
                )
            )

    return insights


def analyze_task_followup(df: pd.DataFrame) -> list[TaskItem]:
    """Identify tasks needing follow-up: overdue, critical, high priority pending."""
    today = datetime.now().date()
    items: list[TaskItem] = []

    for _, row in df.iterrows():
        tid = str(row["task_id"])
        mid = str(row["merchant_id"])
        ttype = str(row["task_type"])
        priority = str(row["priority"])
        status = str(row["status"])
        deadline_str = str(row["deadline"])
        desc = str(row["description"])

        urgency = "normal"
        if status == "overdue":
            urgency = "critical"
        elif status == "pending" and priority in ("critical", "high"):
            try:
                deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                days_left = (deadline_date - today).days
                if days_left <= 3:
                    urgency = "critical" if days_left < 0 else "high"
                elif days_left <= 7:
                    urgency = "medium"
            except ValueError:
                pass

        if status in ("completed", "in_progress"):
            continue

        items.append(
            TaskItem(
                task_id=tid,
                merchant_id=mid,
                task_type=ttype,
                priority=priority,
                status=status,
                deadline=deadline_str,
                description=desc,
                urgency=urgency,
            )
        )

    items.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "normal": 3}.get(x.urgency, 4))
    return items


def generate_ops_suggestions(
    anomalies: list[ProductAnomaly],
    insights: list[CampaignInsight],
    tasks: list[TaskItem],
) -> list[str]:
    """Generate a prioritized list of ops suggestions."""
    suggestions: list[str] = []

    urgent_tasks = [t for t in tasks if t.urgency in ("critical", "high")]
    if urgent_tasks:
        suggestions.append(f"优先处理 {len(urgent_tasks)} 项紧急/高优任务，包括: {', '.join(t.task_id for t in urgent_tasks[:5])}")

    low_stock = [a for a in anomalies if a.anomaly_type == "low_stock"]
    if low_stock:
        suggestions.append(f"立即补货 {len(low_stock)} 款低库存商品: {', '.join(a.product_id for a in low_stock[:5])}")

    low_roi_campaigns = [i for i in insights if i.roi < 3.0]
    if low_roi_campaigns:
        suggestions.append(f"评估 {len(low_roi_campaigns)} 个低 ROI 活动是否继续投放")

    high_refund = [a for a in anomalies if a.anomaly_type == "high_refund_rate"]
    if high_refund:
        suggestions.append(f"关注 {len(high_refund)} 款高退款率商品，排查质量或描述问题")

    low_rating = [a for a in anomalies if a.anomaly_type == "low_rating"]
    if low_rating:
        suggestions.append(f"跟进 {len(low_rating)} 款低评分商品的差评分析和改进")

    if not suggestions:
        suggestions.append("当前运营数据整体健康，建议持续监控关键指标变化")

    return suggestions


def generate_next_actions(
    anomalies: list[ProductAnomaly],
    insights: list[CampaignInsight],
    tasks: list[TaskItem],
) -> list[str]:
    """Generate a concrete next-action checklist."""
    actions: list[str] = []

    for t in tasks:
        if t.urgency == "critical":
            actions.append(f"[紧急] {t.task_id}: {t.description}（截止 {t.deadline}）")
    for t in tasks:
        if t.urgency == "high":
            actions.append(f"[高优] {t.task_id}: {t.description}（截止 {t.deadline}）")
    for a in anomalies[:10]:
        actions.append(f"[商品] {a.product_id} {a.title}: {a.suggestion}")
    for i in insights[:5]:
        actions.append(f"[活动] {i.campaign_id} {i.campaign_name}: {i.suggestion}")

    if not actions:
        actions.append("当前无紧急事项，按日常节奏执行运营计划")

    return actions
