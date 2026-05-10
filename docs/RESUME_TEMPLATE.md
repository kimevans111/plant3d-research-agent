# 简历描述模板

## 中文版本

**Plant3D Research Agent｜三维植物点云分割科研 Agent**

- 基于 FastAPI + Streamlit 构建科研 Agent Demo，支持训练日志上传、指标解析、RAG 文档问答、训练曲线绘制和 Markdown 实验报告生成。
- 设计轻量 Tool Calling 编排流程，将日志解析、指标诊断、绘图、RAG 检索和报告生成封装为可测试工具，支持无 API Key 的 mock LLM fallback。
- 实现本地 JSON 向量库与 Chroma 可选后端，支持论文笔记/实验记录切分、索引、top-k 召回和带来源 citation 的回答。
- 针对 3D plant point cloud segmentation 场景解析 mIoU、F1、OA、leaf/stem IoU 等指标，并诊断过拟合、训练震荡和类别不平衡问题。
- 补充 pytest、Docker Compose、一键 Demo 和架构/面试文档，提升项目可复现性和作品集展示质量。

## English Version

**Plant3D Research Agent | AI Agent for 3D Plant Point Cloud Segmentation Experiments**

- Built a FastAPI + Streamlit research Agent that analyzes training logs, retrieves research notes with RAG, plots metric curves, and generates Markdown experiment reports.
- Designed a lightweight tool-calling workflow for log parsing, metric diagnosis, plotting, retrieval, and report generation with a mock LLM fallback for keyless demos.
- Implemented a local JSON vector store with optional Chroma backend for document chunking, indexing, top-k retrieval, and citation-based answers.
- Parsed domain metrics including mIoU, F1, OA, leaf IoU, and stem IoU to detect overfitting, metric oscillation, and class imbalance in plant point cloud segmentation.
- Added pytest coverage, Docker Compose, one-command demo scripts, and interview-facing documentation for portfolio delivery.
