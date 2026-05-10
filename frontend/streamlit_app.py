"""Streamlit frontend for Plant3D Research Agent."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def upload_to_backend(file_obj: Any) -> dict[str, Any]:
    files = {"file": (file_obj.name, file_obj.getvalue())}
    response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=120)
    response.raise_for_status()
    return response.json()


def show_agent_result(result: dict[str, Any]) -> None:
    st.markdown(result.get("answer", ""))

    figures = result.get("figures") or []
    if figures:
        st.subheader("Generated Figures")
        for figure in figures:
            path = Path(figure)
            if path.exists():
                st.image(str(path), caption=path.name, use_container_width=True)
            else:
                st.write(figure)

    citations = result.get("citations") or []
    if citations:
        st.subheader("Citations")
        for item in citations:
            with st.expander(f"{item.get('source', 'unknown')} | score={item.get('score', 0):.3f}"):
                st.write(item.get("chunk", ""))

    report_path = result.get("report_path")
    if report_path:
        path = Path(report_path)
        if path.exists():
            st.download_button(
                "Download Markdown Report",
                data=path.read_bytes(),
                file_name=path.name,
                mime="text/markdown",
            )
        else:
            st.info(f"Report path: {report_path}")


def show_rag_eval_result(result: dict[str, Any]) -> None:
    """Render RAG evaluation metrics and report downloads."""
    summary = result.get("summary", {})
    st.subheader("Summary Metrics")
    st.dataframe(
        [{"metric": key, "value": value} for key, value in summary.items() if key != "metrics_by_category"],
        use_container_width=True,
    )

    metrics_by_category = result.get("metrics_by_category") or summary.get("metrics_by_category") or {}
    if metrics_by_category:
        st.subheader("Metrics by Category")
        rows = [{"category": category, **values} for category, values in metrics_by_category.items()]
        st.dataframe(rows, use_container_width=True)

    failure_cases = result.get("failure_cases") or []
    if failure_cases:
        st.subheader("Failure Cases")
        for item in failure_cases[:5]:
            with st.expander(f"{item.get('id')} | score={item.get('average_score', 0):.3f} | {item.get('question')}"):
                st.write("Expected sources:", item.get("expected_sources", []))
                st.write("Retrieved sources:", item.get("retrieved_sources", []))
                st.write("Missing keywords:", item.get("missing_keywords", []))
                st.write("Failure reason:", item.get("failure_reason"))

    col_report, col_detail = st.columns(2)
    with col_report:
        _download_backend_file("Download RAG Eval Report", result.get("report_path"), "/rag-eval/reports")
    with col_detail:
        _download_backend_file("Download RAG Eval Details", result.get("detail_path"), "/rag-eval/results")


def _download_backend_file(label: str, file_path: str | None, endpoint: str) -> None:
    if not file_path:
        return
    filename = Path(file_path).name
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}/{filename}", timeout=30)
        response.raise_for_status()
        st.download_button(label, data=response.content, file_name=filename)
    except Exception:
        st.info(f"{label}: {file_path}")


def main() -> None:
    st.set_page_config(page_title="Plant3D Research Agent", layout="wide")
    st.title("Plant3D Research Agent")

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    with st.sidebar:
        st.caption(f"Backend: {BACKEND_URL}")
        try:
            health = requests.get(f"{BACKEND_URL}/health", timeout=5).json()
            st.success(f"API {health.get('status', 'ok')}")
        except Exception:
            st.error("Backend is not reachable.")

    uploaded = st.file_uploader(
        "Upload experiment files",
        type=["txt", "log", "md", "csv", "json", "pdf"],
        accept_multiple_files=True,
    )
    if st.button("Upload Files", type="primary", disabled=not uploaded):
        for file_obj in uploaded or []:
            try:
                record = upload_to_backend(file_obj)
                st.session_state.uploaded_files.append(record)
                st.success(f"Uploaded {record['filename']}")
            except Exception as exc:
                st.error(f"Upload failed for {file_obj.name}: {exc}")

    uploaded_records = st.session_state.uploaded_files
    if uploaded_records:
        st.dataframe(uploaded_records, use_container_width=True)

    col_index, col_log = st.columns(2)
    with col_index:
        if st.button("Build RAG Knowledge Base"):
            try:
                result = post_json("/build-index", {})
                st.json(result)
            except Exception as exc:
                st.error(f"Failed to build index: {exc}")

    with col_log:
        log_options = [
            item["filename"]
            for item in uploaded_records
            if Path(item["filename"]).suffix.lower() in {".log", ".txt"}
        ]
        selected_log = st.selectbox("Training log", options=log_options) if log_options else None
        if st.button("Analyze Log", disabled=not selected_log):
            try:
                result = post_json("/analyze-log", {"filename": selected_log})
                show_agent_result(result)
            except Exception as exc:
                st.error(f"Log analysis failed: {exc}")

    st.subheader("Ask Research Agent")
    query = st.text_area(
        "Question",
        value="Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion？",
        height=100,
    )
    task_type = st.selectbox(
        "Task type",
        options=["auto", "doc_qa", "log_analysis", "model_compare", "report_generation", "general_advice"],
    )
    selectable_paths = [item["saved_path"] for item in uploaded_records]
    selected_paths = st.multiselect("Optional files for this question", selectable_paths)

    if st.button("Ask Agent", type="primary", disabled=not query.strip()):
        payload = {
            "query": query,
            "file_paths": selected_paths,
            "task_type": None if task_type == "auto" else task_type,
        }
        try:
            result = post_json("/ask", payload)
            show_agent_result(result)
        except Exception as exc:
            st.error(f"Agent request failed: {exc}")

    st.subheader("RAG Evaluation")
    with st.form("rag_eval_form"):
        eval_file = st.text_input("Eval file", value="examples/eval/rag_eval_questions.jsonl")
        docs_dir = st.text_input("Docs directory", value="examples")
        top_k = st.slider("top_k", min_value=1, max_value=10, value=3)
        retriever = st.selectbox("Retriever", options=["auto", "keyword", "json", "chroma"], index=0)
        use_agent_answer = st.checkbox("Use Agent answer generation", value=False)
        rebuild_index = st.checkbox("Rebuild index", value=False)
        submitted = st.form_submit_button("Run RAG Evaluation", type="primary")

    if submitted:
        payload = {
            "eval_file": eval_file,
            "docs_dir": docs_dir,
            "top_k": top_k,
            "use_agent_answer": use_agent_answer,
            "retriever": retriever,
            "rebuild_index": rebuild_index,
        }
        try:
            st.session_state.rag_eval_result = post_json("/rag-eval/run", payload)
        except Exception as exc:
            st.error(f"RAG evaluation failed: {exc}")

    if st.session_state.get("rag_eval_result"):
        show_rag_eval_result(st.session_state.rag_eval_result)


if __name__ == "__main__":
    main()
