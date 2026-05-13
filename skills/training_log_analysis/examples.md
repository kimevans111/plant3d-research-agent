# Training Log Analysis Examples

## 1. Analyze a training log

User: "分析 examples/sample_train.log，给出 best mIoU、best F1 和主要问题。"

Expected skill behavior:

- Select `training_log_analysis`.
- Run `parse_training_log`, `summarize_metrics`, and `generate_training_curves`.
- Report metrics only if parsed from the log.

## 2. Explain late F1 fluctuation

User: "为什么我的 F1 后期震荡？"

Expected skill behavior:

- Inspect F1 series and validation loss trend.
- Mention fluctuation only if the metric series shows unstable values.
- Suggest learning-rate reduction, augmentation check, or class-balance review when supported.

## 3. Diagnose low stem IoU

User: "stem IoU 为什么低？"

Expected skill behavior:

- Compare leaf IoU and stem IoU.
- Connect low stem IoU to thin structure, class imbalance, and boundary confusion only as evidence-backed hypotheses.

## 4. Check overfitting

User: "训练后期 loss 下降但验证指标变差，这是过拟合吗？"

Expected skill behavior:

- Compare train/val loss and validation metrics.
- Return "possible overfitting" only when validation behavior supports it.

## 5. Generate a report

User: "把日志分析结果生成 Markdown 报告。"

Expected skill behavior:

- Generate figures if possible.
- Call `generate_markdown_report`.
- Include parser warnings and missing metrics when present.
