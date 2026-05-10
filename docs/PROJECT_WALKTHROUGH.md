# 项目讲解稿

## 30 秒版本

Plant3D Research Agent 是一个面向三维植物点云分割实验的科研 Agent。它可以上传训练日志和论文笔记，自动解析 mIoU、F1、leaf/stem IoU 等指标，调用诊断规则和绘图工具生成训练曲线，再结合 RAG 检索研究笔记，输出带来源的分析回答和 Markdown 实验报告。

## 2 分钟版本

这个项目解决的是科研实验分析自动化问题。三维植物点云分割实验会产生很多训练日志和指标文件，人工看日志很慢，也容易忽略训练震荡、过拟合和 stem 类别表现差等问题。

我的实现是 FastAPI + Streamlit + Agent tools + RAG。FastAPI 负责上传和接口，Streamlit 负责 Demo，Agent 负责根据 query 和文件类型路由任务。日志分析会调用 parser、metric analyzer、plotter 和 report generator；论文或笔记问答会调用 RAG retriever，并把 source snippet 返回给用户。

这个项目不是单纯聊天机器人，因为核心结果来自确定性工具：指标由 parser 抽取，曲线由 Matplotlib 生成，报告由模板汇总，RAG 回答带 citation。LLM provider 是可选增强，默认 mock 模式也能完整运行。

## 5 分钟版本

1. 背景：我的研究场景是 3D plant point cloud semantic segmentation，关注 leaf/stem boundary、thin stem、class imbalance 和 mIoU/F1。
2. 问题：日志、论文笔记和实验表格分散，人工总结影响调参效率。
3. 架构：FastAPI 接口层，ResearchAgent 编排层，tools 工具层，rag 检索层，llm provider 层，Streamlit 展示层。
4. 工作流：上传日志 -> 解析 metrics_series -> 诊断训练动态 -> 生成曲线 -> 检索上下文 -> 生成 Markdown report。
5. 工程质量：支持 pytest、Docker Compose、一键 demo、无 API Key fallback、路径安全校验和结构化响应。
6. 取舍：没有一开始引入重型 Agent 框架，而是先用可测试的 Python 编排证明 Agent workflow，再保留后续接 LangGraph/真实 embedding 的空间。

## Demo 讲解顺序

```bash
python scripts/run_demo.py
```

然后展示：

- 控制台中的 indexed chunks、used tools 和 report path。
- `reports/` 中生成的 Markdown 报告。
- `reports/figures/` 中生成的曲线图。
- `docs/ARCHITECTURE.md` 中的架构图和时序图。
