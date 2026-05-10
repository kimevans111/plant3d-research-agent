# Plant3D Research Agent 项目现状理解

## 项目定位

Plant3D Research Agent 是项目一。它面向三维植物点云语义分割实验，核心目标是把训练日志、实验表格和论文/笔记资料组织成一个可运行的科研分析 Agent。

## 已具备功能

- FastAPI 后端：文件上传、日志分析、RAG 索引构建、Agent 问答、报告下载。
- Streamlit 前端：上传实验文件、构建知识库、分析日志、展示图表/引用/报告。
- Tool Calling 编排：`ResearchAgent` 根据任务类型调用日志解析、指标分析、绘图、报告生成、模型对比和 RAG 检索。
- RAG：支持本地 JSON 向量库，保留 Chroma 后端，默认使用确定性 hashing embedding，保证无 API Key 可运行。
- 日志分析：解析 epoch、loss、mIoU、F1、OA、leaf/stem IoU、best metric 等指标。
- 报告生成：输出 Markdown 报告到 `reports/`，曲线图输出到 `reports/figures/`。
- 测试：已有 parser、metric analyzer、report generator 测试。

## 可运行部分

- `pytest` 可以跑通核心测试。
- `uvicorn app.main:app --reload` 可以启动后端。
- `streamlit run frontend/streamlit_app.py` 可以启动前端。
- `python scripts/run_demo.py` 可以直接跑样例日志分析和 RAG QA。
- `docker compose up --build` 可以同时启动 FastAPI 和 Streamlit。

## 仍像 Demo 的地方

- RAG 默认 embedding 是 hashing 向量，便于演示但语义召回不如真实 embedding 模型。
- Agent 编排是轻量 Python 规则流，不是完整多轮 planner/executor 框架。
- 前端偏 MVP，缺少更完整的实验管理、历史记录、对比看板。
- 对点云本体的可视化还没有接入，例如 PLY/PCD 点云渲染、错误区域可视化。
- 日志解析依赖正则规则，对未知训练框架日志仍需要补模板。

## 影响实习面试认可度的点

- 需要清楚说明它不是普通聊天机器人，而是“任务识别 + 工具调用 + RAG + 结构化报告”的科研 Agent。
- 需要展示完整 Demo 路径：上传日志、生成曲线、诊断问题、生成报告、构建 RAG、回答论文问题。
- 需要能讲清楚 RAG 的取舍：本地 JSON 向量库保证可跑，Chroma/真实 embedding 是后续增强。
- 需要解释 Tool Calling 的边界：什么时候调用 parser，什么时候调用 retriever，什么时候生成 report。
- 需要承认不足：不是大规模 Agent 框架，但工程结构清晰、可测试、可扩展。

## 最优先补强的 5 个点

1. 作品集级 README 和 docs，降低面试官理解成本。
2. 架构图、时序图和 Agent 执行轨迹，方便讲解工作流。
3. 一键 Demo、Docker Compose 和 API 冒烟测试，证明项目可运行。
4. 面试学习文档、项目讲解稿和 Q&A，帮助把项目讲成岗位能力。
5. 后续规划中加入真实 embedding、实验 registry、点云可视化和多实验对比。
