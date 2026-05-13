"""Pydantic schemas for the FastAPI backend."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str
    file_type: str
    size: int
    saved_path: str


class AnalyzeLogRequest(BaseModel):
    filename: str | None = None
    file_path: str | None = None
    query: str = "Analyze this 3D plant point cloud segmentation training log."


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    file_paths: list[str] | None = None
    task_type: str | None = None


class BuildIndexRequest(BaseModel):
    input_dir: str | None = None
    chunk_size: int = 900
    overlap: int = 150


class RagEvalRunRequest(BaseModel):
    eval_file: str = "examples/eval/rag_eval_questions.jsonl"
    docs_dir: str = "examples"
    top_k: int = Field(default=3, ge=1, le=20)
    use_agent_answer: bool = False
    retriever: str = "auto"
    rebuild_index: bool = False


class SkillSelectRequest(BaseModel):
    query: str = Field(..., min_length=1)
    file_paths: list[str] | None = None
    task_type: str | None = None


class AgentResponse(BaseModel):
    answer: str
    used_tools: list[str]
    citations: list[dict[str, Any]] = []
    figures: list[str] = []
    report_path: str | None = None
    metrics: dict[str, Any] | None = None
    parsed_log: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    project: str


class EcommerceRunRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query about e-commerce operations.")


class EcommerceReportRequest(BaseModel):
    report_type: str = Field(default="daily", description="Report type: daily, product, campaign, task.")
