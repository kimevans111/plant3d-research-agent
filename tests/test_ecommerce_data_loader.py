from ecommerce_ops.data_loader import load_all, load_campaigns, load_products, load_tasks


def test_load_products() -> None:
    df = load_products()
    assert len(df) >= 30
    assert "product_id" in df.columns
    assert "price" in df.columns
    assert "conversion_rate" in df.columns


def test_load_campaigns() -> None:
    df = load_campaigns()
    assert len(df) >= 10
    assert "campaign_id" in df.columns
    assert "roi" in df.columns


def test_load_tasks() -> None:
    df = load_tasks()
    assert len(df) >= 15
    assert "task_id" in df.columns
    assert "priority" in df.columns


def test_load_all() -> None:
    prods, camps, tasks = load_all()
    assert len(prods) >= 30
    assert len(camps) >= 10
    assert len(tasks) >= 15
