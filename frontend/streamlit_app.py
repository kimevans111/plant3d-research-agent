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


if __name__ == "__main__":
    main()
