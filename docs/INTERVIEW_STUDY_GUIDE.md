# AI Agent / RAG 实习面试学习文档

## 1. Agent 基础

- Agent = LLM 或规则决策器 + 工具 + 记忆/上下文 + 执行控制。
- 本项目中 Agent 的核心是 `ResearchAgent.run()`：先识别任务，再选择工具，最后聚合结构化结果。
- 面试要强调：可控性和可测试性比“看起来智能”更重要。

## 2. Tool Calling

本项目工具包括：

- `parse_training_log`：把非结构化日志转成结构化指标。
- `summarize_metrics`：生成指标摘要、诊断和建议。
- `generate_training_curve`：生成曲线图。
- `rag_retrieve_context`：检索相关研究笔记。
- `generate_markdown_report`：生成报告。

常见追问：

- 如何避免工具乱调？使用 task type、文件后缀、参数校验和异常 fallback。
- 如何验证工具结果？pytest 覆盖 parser、metrics、report、API/RAG 冒烟流。

## 3. RAG 基础

RAG 流程：

1. Load documents。
2. Split chunks。
3. Embed chunks。
4. Store vectors。
5. Query embedding。
6. Similarity search。
7. Compose answer with citations。

本项目默认使用 hashing embedding + JSON vector store，优点是无外部依赖、演示稳定；缺点是语义能力有限。生产增强可以换成 OpenAI-compatible embedding、bge-m3、text-embedding-3-large 或本地 embedding 模型。

## 4. 后端工程

- FastAPI 用于上传、分析、问答、报告下载。
- Pydantic schema 保证请求和响应结构清晰。
- `_ensure_within_project()` 防止路径穿越。
- Docker Compose 同时启动 backend/frontend，降低 Demo 环境成本。

## 5. 日志分析与科研场景

需要能解释这些指标：

- mIoU：语义分割常用主指标，关注类别平均 IoU。
- F1：precision 和 recall 的调和平均，对边界和小目标敏感。
- OA：整体点级准确率，可能被大类主导。
- leaf/stem IoU gap：植物点云中常见类别不平衡和细结构问题。

## 6. 项目可优化方向

- 接真实 embedding 和 reranker。
- 增加 experiment registry 和多实验对比。
- 增加点云可视化。
- 增加异步任务队列，处理大文件和长报告生成。
- 引入 LangGraph 状态机，支持可恢复多步 Agent。
