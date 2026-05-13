# Training Log Analysis Skill

## Purpose

Analyze deep learning training logs for 3D plant point cloud segmentation experiments. The skill extracts metrics, diagnoses training behavior, generates curves, and prepares Markdown reports.

## When to use

Use this skill when the user uploads or references `.log`, `.txt`, `.csv`, or `.json` training records, or asks about best mIoU, best F1, loss trends, training fluctuation, overfitting, class imbalance, leaf IoU, stem IoU, or tuning suggestions.

## Inputs

- `query`: user question or task instruction.
- `file_paths`: optional training log, metrics CSV, or JSON paths.
- `task_type`: optional explicit route such as `log_analysis`.
- `output_dir`: optional report output directory.

## Outputs

- Parsed metrics and metric series.
- Summary of best epoch, best mIoU, best F1, loss trend, and class-wise signals.
- Diagnosis with evidence.
- Suggested next actions.
- Optional figures and Markdown report path.
- `used_tools` trace.

## Internal tools

- `parse_training_log`
- `summarize_metrics`
- `diagnose_training`
- `generate_training_curves`
- `generate_markdown_report`

## Execution steps

1. Validate file paths and supported suffixes.
2. Parse metrics from the log or table.
3. Summarize best metrics and training dynamics.
4. Diagnose fluctuation, overfitting, class imbalance, and leaf/stem gaps from parsed values.
5. Generate curves when metric series are available.
6. Generate a Markdown report when requested.
7. Return evidence-backed suggestions and a trace of tools used.

## Failure handling

- If no log is available, return a clear missing-file error.
- If a metric is absent, mark it as `unknown` or `not available`.
- If plots cannot be generated, return the parsed metric summary without failing the entire skill.
- If a file is malformed, include parser warnings and continue with recoverable fields.

## Constraints

- Do not invent metrics.
- Every diagnosis must be supported by parser output or provided data.
- Missing metrics must be explicitly marked.
- Tuning suggestions must cite observed evidence such as loss divergence, F1 oscillation, or class-wise IoU gaps.
- The skill must work without an API key.

## Example queries

- "分析这个训练日志，找出 best mIoU 和 best F1。"
- "为什么我的 F1 后期震荡？"
- "stem IoU 为什么明显低于 leaf IoU？"
- "这次训练是否过拟合？"
- "生成一份 Markdown 训练复盘报告。"

## Engineering notes

- This skill separates high-level training analysis from low-level parser and plotting tools.
- The Agent chooses the skill, while the skill owns the workflow and evidence rules.
- The implementation avoids hallucinating metrics because numeric claims come from parser output.
- The `used_tools` trace makes the workflow auditable.
- It can be extended later with more parsers or experiment-registry storage without changing the Agent interface.
