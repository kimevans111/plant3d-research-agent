# Agent 执行轨迹示例

## 场景一：训练日志分析

用户输入：

```text
Why is stem IoU lower than leaf IoU?
file_paths = ["examples/sample_train.log"]
```

执行轨迹：

| Step | Action | Tool | Output |
| --- | --- | --- | --- |
| 1 | 判断任务类型 | `classify_task` | `log_analysis` |
| 2 | 读取日志 | `parse_training_log` | `metrics_series`, `best_miou`, `best_f1` |
| 3 | 指标诊断 | `summarize_metrics` | 过拟合/震荡/leaf-stem gap 等诊断 |
| 4 | 绘图 | `generate_training_curve` | loss、mIoU、F1 曲线 PNG |
| 5 | 召回上下文 | `rag_retrieve_context` | 相关论文笔记片段 |
| 6 | 生成报告 | `generate_markdown_report` | `reports/report_sample_train.md` |
| 7 | 返回结果 | API response | answer、used_tools、figures、report_path |

典型 `used_tools`：

```json
[
  "parse_training_log",
  "summarize_metrics",
  "generate_training_curve",
  "rag_retrieve_context",
  "generate_markdown_report"
]
```

说明：只要用户携带日志文件且没有明确要求 `paper/document/RAG`，解释型 `why` 问题也会进入日志分析链路，避免忽略已提供的日志文件。

## 场景二：RAG 文档问答

用户输入：

```text
Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion?
```

执行轨迹：

| Step | Action | Tool | Output |
| --- | --- | --- | --- |
| 1 | 判断任务类型 | `classify_task` | `doc_qa` |
| 2 | 向量检索 | `rag_retrieve_context` | top-k chunks |
| 3 | 组织回答 | `_compose_rag_answer` 或 LLM provider | 带来源的研究解释 |
| 4 | 返回结果 | API response | answer、citations、used_tools |

面试讲解重点：Agent 的可信度来自工具输出和 citation，而不是凭空生成。
