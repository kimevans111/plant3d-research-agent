from ecommerce_ops.tools import (
    check_product_anomalies,
    generate_merchant_message,
    generate_ops_report,
    list_pending_tasks,
    review_campaign_performance,
)


def test_check_product_anomalies() -> None:
    anomalies, preview = check_product_anomalies()
    assert len(anomalies) > 0, "Should detect at least one anomaly"
    assert len(preview) > 0
    first = anomalies[0]
    assert first.product_id
    assert first.anomaly_type
    assert first.reason
    assert first.suggestion


def test_review_campaign_performance() -> None:
    insights, preview = review_campaign_performance()
    assert len(insights) > 0, "Should detect at least one campaign issue"
    assert len(preview) > 0
    first = insights[0]
    assert first.campaign_id
    assert first.roi is not None
    assert first.insight


def test_list_pending_tasks() -> None:
    tasks, preview = list_pending_tasks()
    assert len(tasks) > 0, "Should have pending/overdue tasks"
    assert len(preview) > 0
    first = tasks[0]
    assert first.task_id


def test_generate_ops_report() -> None:
    data = generate_ops_report(report_type="daily")
    assert data["report_type"] == "daily"
    assert len(data["product_anomalies"]) > 0
    assert len(data["campaign_insights"]) > 0
    assert len(data["pending_tasks"]) > 0
    assert len(data["suggestions"]) > 0
    assert len(data["next_actions"]) > 0


def test_generate_merchant_message() -> None:
    anomalies, _ = check_product_anomalies()
    tasks, _ = list_pending_tasks()
    msg = generate_merchant_message(anomalies=anomalies, tasks=tasks)
    assert "商家运营提醒" in msg
    assert len(msg) > 100


def test_generate_merchant_message_empty() -> None:
    msg = generate_merchant_message(anomalies=[], tasks=[])
    assert "当前无紧急运营事项" in msg
