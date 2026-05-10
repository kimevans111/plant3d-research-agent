from pathlib import Path

from tools.log_parser import parse_training_log
from tools.metric_analyzer import summarize_metrics


ROOT = Path(__file__).resolve().parents[1]


def test_summarize_metrics_returns_diagnosis_and_suggestions() -> None:
    parsed = parse_training_log(ROOT / "examples" / "sample_train.log")
    summary = summarize_metrics(parsed)

    assert "Best mIoU" in summary["summary"]
    assert summary["key_metrics"]["final_epoch"] == 36
    assert summary["diagnosis"]
    assert summary["suggestions"]
    assert any("overfitting" in item.lower() or "Stem IoU" in item for item in summary["diagnosis"])
