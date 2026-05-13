"""E-commerce Ops Agent — lightweight query routing and multi-role orchestration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ecommerce_ops.report import generate_markdown_report
from ecommerce_ops.schemas import EcommerceAgentResponse, ToolTrace
from ecommerce_ops.tools import (
    check_product_anomalies,
    generate_merchant_message,
    generate_ops_report,
    list_pending_tasks,
    review_campaign_performance,
)


TOOL_ROUTING = {
    "product_check": {
        "keywords": ["库存", "转化率", "商品", "退款", "评分", "跟单", "异常", "缺货", "滞销"],
        "tool_name": "check_product_anomalies",
    },
    "campaign_review": {
        "keywords": ["活动", "roi", "投放", "预算", "订单", "推广", "大促", "营销", "ctr"],
        "tool_name": "review_campaign_performance",
    },
    "task_followup": {
        "keywords": ["任务", "跟进", "截止", "待办", "提醒", "商家通知", "催办", "工单"],
        "tool_name": "list_pending_tasks",
    },
    "ops_report": {
        "keywords": ["日报", "报告", "总结", "运营建议", "周报", "复盘", "总览"],
        "tool_name": "generate_ops_report",
    },
}

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "ecommerce_ops"


class EcommerceOpsAgent:
    """Lightweight agent for e-commerce ops scenario simulation.

    Routes queries to tools via keyword matching, executes analysis,
    and returns structured responses with multi-role trace.
    """

    def __init__(self, reports_dir: Path | str | None = None) -> None:
        self.reports_dir = Path(reports_dir) if reports_dir else REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, query: str) -> EcommerceAgentResponse:
        """Route query to the best tool, execute, and return structured response."""
        lowered = query.lower()
        selected = _classify_query(lowered)

        trace: list[ToolTrace] = []

        if selected == "product_check":
            trace, answer, data, report_path = self._handle_product_check(trace)
        elif selected == "campaign_review":
            trace, answer, data, report_path = self._handle_campaign_review(trace)
        elif selected == "task_followup":
            trace, answer, data, report_path = self._handle_task_followup(trace)
        else:
            trace, answer, data, report_path = self._handle_ops_report(trace)

        return EcommerceAgentResponse(
            answer=answer,
            selected_tool=TOOL_ROUTING[selected]["tool_name"],
            used_tools=[t.action for t in trace],
            trace=trace,
            report_path=report_path,
            data_preview=data,
        )

    def _handle_product_check(self, trace: list[ToolTrace]) -> tuple[list[ToolTrace], str, list[dict[str, Any]], str | None]:
        trace.append(ToolTrace(role="data_analyst", action="check_product_anomalies", status="running", detail="Loading and analyzing product data"))
        anomalies, preview = check_product_anomalies()
        trace[-1].status = "success"
        trace[-1].detail = f"Detected {len(anomalies)} anomalies"

        if not anomalies:
            return trace, "当前所有商品运营指标正常，未发现明显异常。", preview, None

        trace.append(ToolTrace(role="copywriter", action="generate_followup_message", status="running", detail="Composing merchant-facing summary"))
        message = generate_merchant_message(anomalies=anomalies)
        trace[-1].status = "success"

        lines = [
            "## 商品数据检查\n",
            f"发现 **{len(anomalies)}** 项商品异常：\n",
        ]
        anomaly_types = {}
        for a in anomalies:
            anomaly_types.setdefault(a.anomaly_type, []).append(a)

        for atype, items in anomaly_types.items():
            type_names = {
                "low_stock": "库存不足",
                "low_conversion_high_exposure": "高曝光低转化",
                "high_refund_rate": "退款率偏高",
                "low_rating": "评分偏低",
            }
            lines.append(f"### {type_names.get(atype, atype)}（{len(items)} 款）")
            for a in items[:5]:
                lines.append(f"- **{a.product_id}** {a.title}: {a.reason}")
                lines.append(f"  → {a.suggestion}")
            lines.append("")

        report_path = self._save_report(query="商品数据检查", body="\n".join(lines))

        trace.append(ToolTrace(role="notifier", action="generate_report", status="success", detail=f"Report saved to {report_path}"))
        return trace, "\n".join(lines), preview, report_path

    def _handle_campaign_review(self, trace: list[ToolTrace]) -> tuple[list[ToolTrace], str, list[dict[str, Any]], str | None]:
        trace.append(ToolTrace(role="data_analyst", action="review_campaign_performance", status="running", detail="Loading and analyzing campaign data"))
        insights, preview = review_campaign_performance()
        trace[-1].status = "success"
        trace[-1].detail = f"Reviewed {len(insights)} campaign issues"

        if not insights:
            return trace, "当前所有在投活动表现正常，ROI 和点击率在合理范围内。", preview, None

        lines = [
            "## 活动复盘\n",
            f"发现 **{len(insights)}** 项活动需要关注：\n",
        ]
        for i in insights:
            lines.append(f"- **{i.campaign_id}** {i.campaign_name}")
            lines.append(f"  - ROI: {i.roi:.2f} | CTR: {i.ctr:.4f} | 花费: {i.spend:.0f}元 | 订单: {i.orders}")
            lines.append(f"  - {i.insight}")
            lines.append(f"  - 建议: {i.suggestion}")
            lines.append("")

        report_path = self._save_report(query="活动复盘", body="\n".join(lines))

        trace.append(ToolTrace(role="notifier", action="generate_report", status="success", detail=f"Report saved to {report_path}"))
        return trace, "\n".join(lines), preview, report_path

    def _handle_task_followup(self, trace: list[ToolTrace]) -> tuple[list[ToolTrace], str, list[dict[str, Any]], str | None]:
        trace.append(ToolTrace(role="data_analyst", action="list_pending_tasks", status="running", detail="Loading and analyzing tasks"))
        tasks, preview = list_pending_tasks()
        trace[-1].status = "success"
        trace[-1].detail = f"Found {len(tasks)} pending/overdue tasks"

        if not tasks:
            return trace, "当前所有运营任务已完成，无待跟进事项。", preview, None

        trace.append(ToolTrace(role="copywriter", action="generate_followup_message", status="running", detail="Composing task follow-up message"))
        lines = [
            "## 运营任务跟进\n",
            f"共 **{len(tasks)}** 项待处理任务：\n",
        ]

        urgency_groups = {"critical": [], "high": [], "medium": [], "normal": []}
        for t in tasks:
            urgency_groups.setdefault(t.urgency, []).append(t)

        urg_names = {"critical": "紧急", "high": "高优", "medium": "中优", "normal": "常规"}
        for urg, items in urgency_groups.items():
            if not items:
                continue
            lines.append(f"### {urg_names.get(urg, urg)}（{len(items)} 项）")
            for t in items[:5]:
                status_tag = "⚠️ 已逾期" if t.status == "overdue" else f"📋 {t.status}"
                lines.append(f"- **{t.task_id}** [{t.priority}] {status_tag} 截止 {t.deadline}")
                lines.append(f"  - {t.description}")
            lines.append("")

        trace[-1].status = "success"
        report_path = self._save_report(query="运营任务跟进", body="\n".join(lines))

        trace.append(ToolTrace(role="notifier", action="generate_report", status="success", detail=f"Report saved to {report_path}"))
        return trace, "\n".join(lines), preview, report_path

    def _handle_ops_report(self, trace: list[ToolTrace]) -> tuple[list[ToolTrace], str, list[dict[str, Any]], str | None]:
        trace.append(ToolTrace(role="data_analyst", action="generate_ops_report", status="running", detail="Generating comprehensive ops report"))
        report_data = generate_ops_report(report_type="daily")
        trace[-1].status = "success"
        trace[-1].detail = f"Report: {len(report_data['product_anomalies'])} anomalies, {len(report_data['campaign_insights'])} insights, {len(report_data['pending_tasks'])} tasks"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"ecommerce_ops_report_{timestamp}.md"
        generate_markdown_report(report_data=report_data, query="商家运营日报", output_path=report_path)

        trace.append(ToolTrace(role="copywriter", action="compose_report_summary", status="success", detail="Composed report summary"))
        trace.append(ToolTrace(role="notifier", action="save_report", status="success", detail=f"Report saved to {report_path}"))

        answer = self._build_report_summary(report_data)
        return (
            trace,
            answer,
            list(report_data.get("data_preview", {}).get("products", [])[:5]) if isinstance(report_data.get("data_preview"), dict) else [],
            str(report_path),
        )

    def _save_report(self, query: str, body: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / f"ecommerce_ops_{timestamp}.md"
        lines = [
            "# E-commerce Ops Agent Report",
            "",
            f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- Query: {query}",
            "",
            body,
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _build_report_summary(self, report_data: dict[str, Any]) -> str:
        anomalies = report_data.get("product_anomalies", [])
        insights = report_data.get("campaign_insights", [])
        tasks = report_data.get("pending_tasks", [])
        suggestions = report_data.get("suggestions", [])
        next_actions = report_data.get("next_actions", [])

        lines = [
            "## 商家运营日报\n",
            f"### 商品异常: {len(anomalies)} 项",
        ]
        for a in anomalies[:5]:
            lines.append(f"- {a.product_id} {a.title}: {a.reason}")
        lines.extend(["", f"### 活动关注: {len(insights)} 项"])
        for i in insights[:5]:
            lines.append(f"- {i.campaign_id} {i.campaign_name}: {i.insight}")
        lines.extend(["", f"### 待跟进任务: {len(tasks)} 项"])
        urgent = [t for t in tasks if t.urgency in ("critical", "high")]
        for t in urgent[:5]:
            lines.append(f"- {t.task_id}: {t.description}")
        lines.extend(["", "### 运营建议"])
        for s in suggestions[:5]:
            lines.append(f"- {s}")
        lines.extend(["", "### 下一步行动"])
        for action in next_actions[:8]:
            lines.append(f"- {action}")

        return "\n".join(lines)


def _classify_query(lowered: str) -> str:
    """Classify query into tool category by keyword scoring."""
    scores: dict[str, int] = {}
    for task_key, config in TOOL_ROUTING.items():
        scores[task_key] = sum(1 for kw in config["keywords"] if kw in lowered)

    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "ops_report"  # default fallback
    return best
