from fastapi.testclient import TestClient

from app.main import app


def test_ecommerce_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/ecommerce/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["module"] == "E-commerce Ops Agent Mini"
    assert len(body["data_files"]) == 3


def test_ecommerce_analyze_product_check() -> None:
    client = TestClient(app)
    response = client.post(
        "/ecommerce/analyze",
        json={"query": "哪些商品库存不足或转化率低？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "check_product_anomalies"
    assert len(body["used_tools"]) >= 2
    assert len(body["trace"]) >= 2
    assert len(body["data_preview"]) > 0


def test_ecommerce_analyze_campaign_review() -> None:
    client = TestClient(app)
    response = client.post(
        "/ecommerce/analyze",
        json={"query": "哪些活动ROI较低？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "review_campaign_performance"


def test_ecommerce_analyze_task_followup() -> None:
    client = TestClient(app)
    response = client.post(
        "/ecommerce/analyze",
        json={"query": "有哪些高优先级任务还没完成？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "list_pending_tasks"


def test_ecommerce_analyze_defaults_to_ops_report() -> None:
    client = TestClient(app)
    response = client.post(
        "/ecommerce/analyze",
        json={"query": "今天天气怎么样？"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_tool"] == "generate_ops_report"
