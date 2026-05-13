# Report Generation Examples

## 1. Training analysis report

User: "生成训练日志分析报告。"

Expected skill behavior:

- Use parsed log metrics and generated figures.
- Save a Markdown report under `reports/`.

## 2. RAG evaluation report

User: "生成 RAG 评估报告。"

Expected skill behavior:

- Use RAG-Eval summary, category metrics, and failure cases.
- Save under `reports/rag_eval/`.

## 3. Model comparison report

User: "把两个模型的训练结果生成对比报告。"

Expected skill behavior:

- Include comparable metrics and clearly label data sources.

## 4. Paper-style result wording

User: "把 mIoU 和 F1 结果写成论文式描述。"

Expected skill behavior:

- Use only supplied metrics.
- Avoid fabricating statistical claims.

## 5. Missing figures

User: "报告里图表路径不存在怎么办？"

Expected skill behavior:

- Skip missing images.
- Add a missing-item note rather than failing the full report.
