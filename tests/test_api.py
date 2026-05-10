from pathlib import Path

from fastapi.testclient import TestClient

from app.main import UPLOADS_DIR, app


ROOT = Path(__file__).resolve().parents[1]


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_and_analyze_log_endpoint() -> None:
    client = TestClient(app)
    sample_path = ROOT / "examples" / "sample_train.log"

    with sample_path.open("rb") as file_obj:
        upload = client.post(
            "/upload",
            files={"file": ("api_sample_train.log", file_obj, "text/plain")},
        )

    assert upload.status_code == 200
    filename = upload.json()["filename"]

    try:
        response = client.post("/analyze-log", json={"filename": filename})

        assert response.status_code == 200
        body = response.json()
        assert "parse_training_log" in body["used_tools"]
        assert body["report_path"]
        assert body["figures"]
    finally:
        (UPLOADS_DIR / filename).unlink(missing_ok=True)


def test_build_index_and_doc_qa_endpoint() -> None:
    client = TestClient(app)

    index_response = client.post(
        "/build-index",
        json={"input_dir": "examples", "chunk_size": 500, "overlap": 80},
    )

    assert index_response.status_code == 200
    assert index_response.json()["chunks"] > 0

    ask_response = client.post(
        "/ask",
        json={
            "query": "Plant-GeoAT boundary confusion",
            "task_type": "doc_qa",
        },
    )

    assert ask_response.status_code == 200
    body = ask_response.json()
    assert "rag_retrieve_context" in body["used_tools"]
    assert body["citations"]


def test_rag_eval_run_endpoint() -> None:
    client = TestClient(app)

    response = client.post(
        "/rag-eval/run",
        json={
            "eval_file": "examples/eval/rag_eval_questions.jsonl",
            "docs_dir": "examples",
            "top_k": 2,
            "use_agent_answer": False,
            "retriever": "keyword",
            "rebuild_index": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["num_questions"] >= 20
    assert body["report_path"].endswith(".md")
