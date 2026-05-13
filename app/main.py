"""FastAPI backend for Plant3D Research Agent."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from agent.research_agent import ResearchAgent
from app.schemas import (
    AgentResponse,
    AnalyzeLogRequest,
    AskRequest,
    BuildIndexRequest,
    EcommerceReportRequest,
    EcommerceRunRequest,
    HealthResponse,
    RagEvalRunRequest,
    SkillSelectRequest,
    UploadResponse,
)
from ecommerce_ops.agent import EcommerceOpsAgent
from ecommerce_ops.schemas import EcommerceHealthResponse
from rag.retriever import build_index
from rag_eval.evaluator import RagEvaluator
from skills.executor import SkillExecutor
from skills.registry import SkillRegistry


BASE_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
RAG_EVAL_DIR = REPORTS_DIR / "rag_eval"
ECOMMERCE_OPS_DIR = REPORTS_DIR / "ecommerce_ops"
SUPPORTED_UPLOAD_SUFFIXES = {".txt", ".log", ".md", ".csv", ".json", ".pdf"}

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RAG_EVAL_DIR.mkdir(parents=True, exist_ok=True)
ECOMMERCE_OPS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Plant3D Research Agent",
    description="Agent backend for 3D plant point cloud segmentation experiment analysis.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _safe_filename(filename: str) -> str:
    clean = Path(filename).name.replace(" ", "_")
    if not clean:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    return clean


def _ensure_within_project(path: Path) -> Path:
    resolved = path.resolve()
    base = BASE_DIR.resolve()
    if resolved != base and base not in resolved.parents:
        raise HTTPException(status_code=400, detail="Path must stay inside the project directory.")
    return resolved


def _resolve_user_path(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        upload_candidate = UPLOADS_DIR / candidate
        root_candidate = BASE_DIR / candidate
        candidate = upload_candidate if upload_candidate.exists() else root_candidate
    resolved = _ensure_within_project(candidate)
    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {value}")
    return resolved


def _agent() -> ResearchAgent:
    return ResearchAgent(uploads_dir=UPLOADS_DIR, reports_dir=REPORTS_DIR, figures_dir=FIGURES_DIR)


@app.get("/")
def root() -> dict[str, str]:
    """Return a minimal project greeting."""
    return {
        "message": "Plant3D Research Agent API",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", project="Plant3D Research Agent")


@app.post("/upload", response_model=UploadResponse)
def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a research file into the uploads directory."""
    filename = _safe_filename(file.filename or "uploaded_file")
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    destination = UPLOADS_DIR / filename
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}") from exc

    return UploadResponse(
        filename=filename,
        file_type=suffix,
        size=destination.stat().st_size,
        saved_path=str(destination),
    )


@app.post("/analyze-log", response_model=AgentResponse)
def analyze_log(request: AnalyzeLogRequest) -> dict[str, Any]:
    """Analyze a selected training log and generate plots/reports."""
    path_value = request.file_path or request.filename
    if not path_value:
        raise HTTPException(status_code=400, detail="filename or file_path is required.")
    path = _resolve_user_path(path_value)
    if path.suffix.lower() not in {".log", ".txt"}:
        raise HTTPException(status_code=400, detail="Log analysis expects a .log or .txt file.")
    return _agent().run(query=request.query, file_paths=[path], task_type="log_analysis")


@app.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest) -> dict[str, Any]:
    """Ask the research agent a question."""
    paths = [_resolve_user_path(path) for path in request.file_paths or []]
    return _agent().run(query=request.query, file_paths=paths, task_type=request.task_type)


@app.post("/build-index")
def build_rag_index(request: BuildIndexRequest | None = None) -> dict[str, Any]:
    """Build a RAG index from uploads or a user-provided project directory."""
    request = request or BuildIndexRequest()
    input_dir = _resolve_user_path(request.input_dir) if request.input_dir else UPLOADS_DIR
    if not input_dir.is_dir():
        raise HTTPException(status_code=400, detail="input_dir must be a directory.")
    try:
        return build_index(input_dir=input_dir, chunk_size=request.chunk_size, overlap=request.overlap)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build RAG index: {exc}") from exc


@app.get("/skills")
def list_skills() -> dict[str, Any]:
    """List lightweight Skill Layer definitions."""
    registry = SkillRegistry(BASE_DIR / "skills")
    return {"skills": [skill.summary() for skill in registry.list_skills()]}


@app.post("/skills/select")
def select_skill(request: SkillSelectRequest) -> dict[str, Any]:
    """Select the most relevant skill for a user query."""
    return SkillExecutor(registry=SkillRegistry(BASE_DIR / "skills")).execute(
        query=request.query,
        file_paths=request.file_paths or [],
        task_type=request.task_type,
    ).to_dict()


@app.get("/skills/{skill_name}")
def get_skill(skill_name: str) -> dict[str, Any]:
    """Return one skill definition summary and Markdown instructions."""
    registry = SkillRegistry(BASE_DIR / "skills")
    skill = registry.get_skill(skill_name)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    payload = skill.summary()
    payload["schema"] = skill.schema
    payload["instructions"] = skill.skill_md
    return payload


@app.get("/reports/{filename}")
def get_report(filename: str) -> FileResponse:
    """Download a generated report or figure from reports/."""
    safe_name = _safe_filename(filename)
    path = _ensure_within_project(REPORTS_DIR / safe_name)
    if not path.exists() or not path.is_file():
        figure_path = _ensure_within_project(FIGURES_DIR / safe_name)
        if figure_path.exists() and figure_path.is_file():
            path = figure_path
        else:
            raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(path)


@app.post("/rag-eval/run")
def run_rag_eval(request: RagEvalRunRequest) -> dict[str, Any]:
    """Run lightweight RAG retrieval evaluation."""
    eval_file = _resolve_user_path(request.eval_file)
    docs_dir = _resolve_user_path(request.docs_dir)
    if not eval_file.is_file() or eval_file.suffix.lower() != ".jsonl":
        raise HTTPException(status_code=400, detail="eval_file must be a .jsonl file.")
    if not docs_dir.is_dir():
        raise HTTPException(status_code=400, detail="docs_dir must be a directory.")
    if request.retriever not in {"auto", "keyword", "json", "chroma"}:
        raise HTTPException(status_code=400, detail="retriever must be one of auto, keyword, json, chroma.")

    try:
        result = RagEvaluator(
            eval_file=eval_file,
            docs_dir=docs_dir,
            output_dir=RAG_EVAL_DIR,
            top_k=request.top_k,
            use_agent_answer=request.use_agent_answer,
            retriever=request.retriever,
            rebuild_index=request.rebuild_index,
        ).run()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to run RAG eval: {exc}") from exc
    return {
        "summary": result["summary"],
        "report_path": result["report_path"],
        "detail_path": result["detail_path"],
        "summary_path": result["summary_path"],
        "trace": result["trace"],
        "metrics_by_category": result.get("metrics_by_category", {}),
        "failure_cases": result.get("failure_cases", [])[:10],
    }


@app.get("/rag-eval/reports/{filename}")
def get_rag_eval_report(filename: str) -> FileResponse:
    """Download a RAG evaluation Markdown report."""
    safe_name = _safe_filename(filename)
    path = _ensure_within_project(RAG_EVAL_DIR / safe_name)
    if path.suffix.lower() != ".md" or not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="RAG eval report not found.")
    return FileResponse(path, media_type="text/markdown")


@app.get("/rag-eval/results/{filename}")
def get_rag_eval_result(filename: str) -> FileResponse:
    """Download a RAG evaluation JSON result file."""
    safe_name = _safe_filename(filename)
    path = _ensure_within_project(RAG_EVAL_DIR / safe_name)
    if path.suffix.lower() != ".json" or not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="RAG eval result not found.")
    return FileResponse(path, media_type="application/json")


# ---------------------------------------------------------------------------
# E-commerce Ops Agent Mini endpoints
# ---------------------------------------------------------------------------

ECOMMERCE_SAMPLE_DATA_DIR = BASE_DIR / "ecommerce_ops" / "sample_data"


@app.get("/ecommerce/health", response_model=EcommerceHealthResponse)
def ecommerce_health() -> EcommerceHealthResponse:
    """Health check for the E-commerce Ops Agent Mini module."""
    data_files = sorted(
        f.name
        for f in ECOMMERCE_SAMPLE_DATA_DIR.iterdir()
        if f.is_file() and f.suffix == ".csv"
    )
    return EcommerceHealthResponse(
        status="ok",
        module="E-commerce Ops Agent Mini",
        data_files=data_files,
    )


@app.post("/ecommerce/analyze")
def ecommerce_analyze(request: EcommerceRunRequest) -> dict[str, Any]:
    """Analyze an e-commerce ops query using mock data."""
    agent = EcommerceOpsAgent(reports_dir=ECOMMERCE_OPS_DIR)
    result = agent.run(query=request.query)
    return result.model_dump()


@app.post("/ecommerce/report")
def ecommerce_report(request: EcommerceReportRequest | None = None) -> dict[str, Any]:
    """Generate a structured e-commerce ops report."""
    request = request or EcommerceReportRequest()
    from ecommerce_ops.tools import generate_ops_report as gen_report
    from ecommerce_ops.report import generate_markdown_report

    data = gen_report(report_type=request.report_type)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = ECOMMERCE_OPS_DIR / f"ecommerce_ops_report_{timestamp}.md"
    generate_markdown_report(
        report_data=data,
        query=f"{request.report_type} report",
        output_path=report_path,
    )
    return {
        "report_path": str(report_path),
        "summary": f"Generated {request.report_type} report with {len(data.get('product_anomalies', []))} anomalies, {len(data.get('campaign_insights', []))} insights, {len(data.get('pending_tasks', []))} tasks.",
        "trace": [
            {"role": "data_analyst", "action": "generate_ops_report", "status": "success"},
            {"role": "notifier", "action": "save_report", "status": "success", "detail": str(report_path)},
        ],
    }


@app.get("/ecommerce/reports/{filename}")
def get_ecommerce_report(filename: str) -> FileResponse:
    """Download a generated e-commerce ops report."""
    safe_name = _safe_filename(filename)
    path = _ensure_within_project(ECOMMERCE_OPS_DIR / safe_name)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="E-commerce ops report not found.")
    return FileResponse(path, media_type="text/markdown")


# Import datetime for the report endpoint
from datetime import datetime  # noqa: E402
