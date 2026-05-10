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
    HealthResponse,
    UploadResponse,
)
from rag.retriever import build_index


BASE_DIR = Path(__file__).resolve().parents[1]
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SUPPORTED_UPLOAD_SUFFIXES = {".txt", ".log", ".md", ".csv", ".json", ".pdf"}

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

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
