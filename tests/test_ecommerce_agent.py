from pathlib import Path

from ecommerce_ops.agent import EcommerceOpsAgent, _classify_query


def test_classify_product_check_queries() -> None:
    queries = [
        "哪些商品库存不足？",
        "哪些商品转化率低但曝光高？",
        "哪些商品退款率偏高？",
        "哪些商品评分低？",
        "找出可能需要运营跟进的商品",
    ]
    for q in queries:
        assert _classify_query(q.lower()) == "product_check", f"Failed for: {q}"


def test_classify_campaign_review_queries() -> None:
    queries = [
        "本周活动效果怎么样？",
        "哪些活动ROI较低？",
        "哪些投放预算超支？",
        "618大促效果如何？",
    ]
    for q in queries:
        assert _classify_query(q.lower()) == "campaign_review", f"Failed for: {q}"


def test_classify_task_followup_queries() -> None:
    queries = [
        "有哪些高优先级任务还没完成？",
        "哪些任务快到截止时间？",
        "给我生成一份今日运营跟进清单",
        "生成一段给商家的提醒文案",
    ]
    for q in queries:
        assert _classify_query(q.lower()) == "task_followup", f"Failed for: {q}"


def test_classify_ops_report_queries() -> None:
    queries = [
        "生成一份商家运营日报",
        "生成运营周报",
        "总结本周运营情况",
    ]
    for q in queries:
        assert _classify_query(q.lower()) == "ops_report", f"Failed for: {q}"


def test_agent_product_check(tmp_path: Path) -> None:
    agent = EcommerceOpsAgent(reports_dir=tmp_path / "reports")
    result = agent.run("哪些商品转化率低但曝光高？")

    assert result.selected_tool == "check_product_anomalies"
    assert "check_product_anomalies" in result.used_tools
    assert len(result.trace) >= 2
    assert "low_conversion" in result.answer or "高曝光低转化" in result.answer
    assert len(result.data_preview) > 0


def test_agent_campaign_review(tmp_path: Path) -> None:
    agent = EcommerceOpsAgent(reports_dir=tmp_path / "reports")
    result = agent.run("本周活动ROI怎么样？")

    assert result.selected_tool == "review_campaign_performance"
    assert "review_campaign_performance" in result.used_tools
    assert len(result.trace) >= 2


def test_agent_task_followup(tmp_path: Path) -> None:
    agent = EcommerceOpsAgent(reports_dir=tmp_path / "reports")
    result = agent.run("有哪些高优先级任务还没完成？")

    assert result.selected_tool == "list_pending_tasks"
    assert "list_pending_tasks" in result.used_tools
    assert len(result.trace) >= 2


def test_agent_ops_report(tmp_path: Path) -> None:
    agent = EcommerceOpsAgent(reports_dir=tmp_path / "reports")
    result = agent.run("生成一份商家运营日报")

    assert result.selected_tool == "generate_ops_report"
    assert "generate_ops_report" in result.used_tools
    assert result.report_path
    assert Path(result.report_path).exists()


def test_agent_trace_has_multi_role(tmp_path: Path) -> None:
    agent = EcommerceOpsAgent(reports_dir=tmp_path / "reports")
    result = agent.run("生成一份商家运营日报")

    roles = {step.role for step in result.trace}
    assert "data_analyst" in roles
    assert len(roles) >= 2, f"Expected multi-role trace, got roles: {roles}"
