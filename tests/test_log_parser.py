from pathlib import Path

from tools.log_parser import parse_training_log


ROOT = Path(__file__).resolve().parents[1]


def test_parse_training_log_extracts_best_metrics() -> None:
    parsed = parse_training_log(ROOT / "examples" / "sample_train.log")

    assert parsed["num_epochs"] == 36
    assert parsed["best_miou"] == 0.886
    assert parsed["best_miou_epoch"] == 24
    assert parsed["best_f1"] == 0.918
    assert parsed["best_f1_epoch"] == 24
    assert len(parsed["metrics_series"]) == 36
    assert parsed["metrics_series"][0]["train_loss"] == 1.432
    assert parsed["metrics_series"][-1]["miou"] == 0.833
