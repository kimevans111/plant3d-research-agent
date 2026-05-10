from pathlib import Path

from tools.report_generator import generate_markdown_report


def test_generate_markdown_report_creates_file(tmp_path: Path) -> None:
    parsed = {
        "source_file": "unit_test.log",
        "best_miou": 0.9,
        "best_miou_epoch": 10,
        "best_f1": 0.88,
        "best_f1_epoch": 9,
    }
    summary = {
        "summary": "Parsed 10 epochs. Best mIoU=0.9000.",
        "key_metrics": {
            "best_miou": 0.9,
            "best_miou_epoch": 10,
            "best_f1": 0.88,
            "best_f1_epoch": 9,
            "final_epoch": 10,
        },
        "diagnosis": ["No severe issue."],
        "suggestions": ["Run one more seed."],
    }

    report_path = generate_markdown_report(
        parsed_log=parsed,
        metrics_summary=summary,
        figures=["reports/figures/unit_test_miou_curve.png"],
        citations=[{"source": "notes.md", "chunk": "Plant-GeoAT uses geometry-aware attention."}],
        output_dir=tmp_path,
    )

    path = Path(report_path)
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Key Metrics" in content
    assert "Plant-GeoAT" in content
