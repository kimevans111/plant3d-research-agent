# Plant3D Research Agent 作品集说明

## 这个项目解决什么问题

三维植物点云分割实验通常会产生训练日志、指标表、论文笔记和实验报告。人工整理这些材料很耗时，而且容易只看单个 best mIoU，忽略训练震荡、leaf/stem 类别差异和过拟合信号。

Plant3D Research Agent 把这些工作串成一个可运行 Agent：上传日志或文档后，系统自动解析指标、调用诊断规则、绘制曲线、检索研究笔记，并生成 Markdown 实验报告。

## 为什么不是普通聊天机器人

普通聊天机器人主要依赖对话生成；本项目的回答来自明确的工程流程：

- 先识别任务类型：日志分析、模型对比、文档 QA 或通用建议。
- 再调用工具：parser、metric analyzer、plotter、report generator、retriever。
- 输出结构化结果：指标摘要、诊断、建议、图表路径、RAG citation、报告路径。
- 没有 API Key 时仍然可运行，LLM 只是增强回答表达，不承担核心计算。

## 和 AI Agent 实习岗位的关系

这个项目对应 AI Agent / 大模型应用开发 / RAG 工程实习中的常见能力：

- Agent 工作流设计：任务路由、工具编排、结果聚合。
- Tool Calling：把自然语言需求落到可验证的 Python 工具。
- RAG：文档加载、切分、向量索引、召回、引用来源。
- 后端工程：FastAPI 接口、文件上传、路径安全、报告下载。
- Demo 工程：Streamlit UI、Docker Compose、一键样例运行、pytest。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Backend | FastAPI, Pydantic, Uvicorn |
| Agent | 轻量任务分类 + Python tool orchestration |
| RAG | document loader, text splitter, local JSON vector store, optional Chroma |
| Metrics | regex parser, pandas, numpy |
| Visualization | Matplotlib |
| Frontend | Streamlit |
| Report | Markdown |
| Test/Deploy | pytest, Docker, Docker Compose |

## 核心功能截图占位说明

建议在投递前补 4 张截图到 `docs/assets/`：

- `01_upload_and_analyze.png`：Streamlit 上传日志并点击 Analyze Log。
- `02_metric_curves.png`：mIoU/F1/loss 曲线。
- `03_rag_qa_citations.png`：RAG QA 与 citation 展示。
- `04_markdown_report.png`：生成的 Markdown report。

## Demo 流程

1. 启动：`docker compose up --build` 或分别运行后端/前端。
2. 上传 `examples/sample_train.log`。
3. 点击 Analyze Log，展示解析指标、诊断、建议和图表。
4. 上传或直接索引 `examples/sample_paper_notes.md`。
5. 点击 Build RAG Knowledge Base。
6. 提问：`Plant-GeoAT 为什么能缓解 leaf-stem boundary confusion?`
7. 展示回答、source snippets 和生成报告。

命令行 Demo：

```bash
python scripts/run_demo.py
```

## 面试时如何介绍

可以用一句话开场：

> 这是一个面向三维植物点云分割实验的科研 Agent，它不是单纯聊天，而是把日志解析、指标诊断、RAG 检索、绘图和报告生成串成了可运行的工具调用工作流。

接着按“问题 -> 架构 -> 工作流 -> 结果 -> 不足”讲：

- 问题：科研实验材料分散，日志和论文信息难以快速转成调参建议。
- 架构：FastAPI + Agent Orchestrator + tools + RAG + Streamlit。
- 工作流：任务识别后调用 parser/analyzer/plotter/retriever/report generator。
- 结果：输出指标摘要、可解释诊断、曲线、引用和 Markdown 报告。
- 不足：默认 embedding 简化，后续可接真实 embedding 和点云可视化。

## 项目亮点

- 面向真实科研场景，而不是通用问答玩具。
- 无 API Key 可完整运行，降低 Demo 风险。
- RAG 和 Tool Calling 都有实际工程路径和测试。
- 输出包含报告、图表和引用，方便面试官验证。
- 保留 Chroma 和 OpenAI-compatible provider 扩展点。

## 项目不足与后续优化

- 接入真实 embedding provider，提高中文/英文混合科研笔记召回质量。
- 增加 experiment registry，支持多次实验横向对比和历史追踪。
- 增加 PLY/PCD 点云可视化和错误区域截图。
- 增加更细的 class-wise confusion matrix 和 boundary F1。
- 引入更正式的 planner/executor 或 LangGraph 类工作流，支持多步自我反思和恢复。
