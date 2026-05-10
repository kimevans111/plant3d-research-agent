"""Run a local portfolio demo for Plant3D Research Agent."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.research_agent import ResearchAgent
from rag.retriever import build_index


def main() -> None:
    """Run sample RAG indexing, log analysis, and document QA."""
    os.environ.setdefault("LLM_PROVIDER", "mock")
    os.environ.setdefault("RAG_PERSIST_DIR", str(ROOT / ".rag_index"))
    os.environ.setdefault("RAG_VECTOR_BACKEND", "simple")

    print("== Plant3D Research Agent Demo ==")
    index_result = build_index(input_dir=ROOT / "examples", persist_dir=ROOT / ".rag_index")
    print(f"Indexed {index_result['documents']} documents into {index_result['chunks']} chunks.")

    agent = ResearchAgent(
        uploads_dir=ROOT / "examples",
        reports_dir=ROOT / "reports",
        figures_dir=ROOT / "reports" / "figures",
    )

    log_result = agent.run(
        query="Analyze this 3D plant point cloud segmentation training log.",
        file_paths=[ROOT / "examples" / "sample_train.log"],
        task_type="log_analysis",
    )
    print("\n-- Log Analysis --")
    print(log_result["answer"].splitlines()[0])
    print(f"Tools: {', '.join(log_result['used_tools'])}")
    print(f"Report: {log_result.get('report_path')}")

    qa_result = agent.run(
        query="Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion?",
        task_type="doc_qa",
    )
    print("\n-- RAG QA --")
    print(qa_result["answer"][:500])
    print(f"Tools: {', '.join(qa_result['used_tools'])}")
    print(f"Citations: {len(qa_result.get('citations', []))}")


if __name__ == "__main__":
    main()
