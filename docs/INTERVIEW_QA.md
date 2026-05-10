# 常见面试问答

## Q1：这个项目为什么算 Agent？

A：它不是只把用户问题发给 LLM，而是会根据任务类型调用不同工具。例如日志分析会调用 parser、metric analyzer、plotter 和 report generator；文档问答会调用 RAG retriever。Agent 的职责是路由、编排和聚合结果。

## Q2：为什么不用 LangChain 或 LangGraph？

A：当前目标是作品集 MVP 和稳定 Demo，所以先用轻量 Python 编排。这样每个工具都可测试、出错点少。后续如果要支持复杂多轮计划、状态恢复和人工确认，可以迁移到 LangGraph。

## Q3：RAG 的默认 embedding 为什么用 hashing？

A：为了保证没有 API Key、没有 GPU、没有模型下载时也能跑通完整流程。它适合 Demo 和工程闭环展示，但语义召回有限。生产环境会替换为真实 embedding 模型和 reranker。

## Q4：如何评价 RAG 质量？

A：可以从 recall@k、citation 命中率、answer faithfulness、人工标注问答集和消融实验评估。当前项目先做工程闭环，后续可以加入标准 QA benchmark。

## Q5：日志解析为什么不用 LLM？

A：指标解析是确定性任务，用正则和结构化 parser 更稳定、更便宜、更容易测试。LLM 更适合解释和总结，不适合做唯一的数值来源。

## Q6：如何防止路径安全问题？

A：后端只允许文件路径解析到项目目录内，并使用 `Path(filename).name` 清理上传文件名，避免路径穿越。

## Q7：如果日志格式完全不同怎么办？

A：可以扩展 `METRIC_ALIASES`、增加 parser template，或者引入一个 LLM-assisted schema extraction 作为 fallback，但最终仍应落到结构化 schema 并测试。

## Q8：这个项目的最大不足是什么？

A：RAG 语义能力和前端实验管理还偏 MVP，点云可视化也未接入。它的优势是工程闭环完整、可运行、可测试，适合作为实习投递项目继续迭代。
