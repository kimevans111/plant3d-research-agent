"""Pydantic schemas for E-commerce Ops Agent Mini."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProductAnomaly(BaseModel):
    """A single product anomaly detected by data check."""

    product_id: str
    title: str
    category: str
    anomaly_type: str
    current_value: float
    threshold: float
    reason: str
    suggestion: str


class CampaignInsight(BaseModel):
    """A single campaign performance insight."""

    campaign_id: str
    campaign_name: str
    product_id: str
    spend: float
    orders: int
    roi: float
    ctr: float
    status: str
    insight: str
    suggestion: str


class TaskItem(BaseModel):
    """A single merchant task entry."""

    task_id: str
    merchant_id: str
    task_type: str
    priority: str
    status: str
    deadline: str
    description: str
    urgency: str = "normal"


class OpsReport(BaseModel):
    """Structured daily ops report."""

    report_type: str
    generated_at: str
    product_anomalies: list[ProductAnomaly] = []
    campaign_insights: list[CampaignInsight] = []
    pending_tasks: list[TaskItem] = []
    suggestions: list[str] = []
    next_actions: list[str] = []


class ToolTrace(BaseModel):
    """Trace entry for a single tool or role action."""

    role: str
    action: str
    status: str
    detail: str = ""


class EcommerceAgentResponse(BaseModel):
    """Structured response from the E-commerce Ops Agent."""

    answer: str
    selected_tool: str
    used_tools: list[str] = []
    trace: list[ToolTrace] = []
    report_path: str | None = None
    data_preview: list[dict[str, Any]] = []


class EcommerceRunRequest(BaseModel):
    """Request body for /ecommerce/analyze."""

    query: str = Field(..., min_length=1, description="Natural language query about e-commerce operations.")


class EcommerceReportRequest(BaseModel):
    """Request body for /ecommerce/report."""

    report_type: str = Field(default="daily", description="Report type: daily, product, campaign, task.")


class EcommerceHealthResponse(BaseModel):
    """Health check for ecommerce module."""

    status: str
    module: str
    data_files: list[str]
