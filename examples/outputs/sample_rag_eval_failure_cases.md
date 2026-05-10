# Sample RAG Eval Failure Cases

## q003 - geometry-aware attention 在植物点云分割里关注哪些局部信息？

- Score: 0.5
- Expected sources: sample_paper_notes.md
- Retrieved sources: sample_paper_notes.md, sample_metrics.csv, sample_train.log
- Missing keywords: geometry-aware attention, neighborhood topology, local surface variation, narrow cylindrical stem structures
- Failure reason: Retrieved context or answer missed many expected keywords.

## q006 - 项目中建议同时报告哪些 segmentation 和 phenotype 指标？

- Score: 0.2639
- Expected sources: sample_paper_notes.md
- Retrieved sources: sample_train.log, sample_train.log, sample_train.log
- Missing keywords: F1-score, RMSE, MAE, R2
- Failure reason: Expected source was not retrieved in top-k.

## q007 - sample metrics 中哪个模型的 mIoU 最高？

- Score: 0.2917
- Expected sources: sample_metrics.csv
- Retrieved sources: sample_train.log, sample_train.log, sample_train.log
- Missing keywords: Plant-GeoAT, PointTransformerV3
- Failure reason: Expected source was not retrieved in top-k.

## q008 - Plant-GeoAT 的 leaf_iou 和 stem_iou 在 sample metrics 中是多少？

- Score: 0.3375
- Expected sources: sample_metrics.csv
- Retrieved sources: sample_train.log, sample_train.log, sample_train.log
- Missing keywords: Plant-GeoAT, 0.854
- Failure reason: Expected source was not retrieved in top-k.

## q012 - thin stem missing 属于哪类常见失败案例？

- Score: 0.2917
- Expected sources: sample_train.log
- Retrieved sources: sample_paper_notes.md, sample_paper_notes.md, sample_paper_notes.md
- Missing keywords: thin stem missing, overlapping leaves
- Failure reason: Expected source was not retrieved in top-k.

## q014 - stem points rare 时可以用哪些训练策略缓解类别不平衡？

- Score: 0.5625
- Expected sources: sample_paper_notes.md
- Retrieved sources: sample_paper_notes.md, sample_paper_notes.md, sample_train.log
- Missing keywords: class-balanced loss, focal loss, stem points are rare
- Failure reason: Retrieved context or answer missed many expected keywords.

## q019 - Agent 在回答研究笔记问题时为什么需要 citation？

- Score: 0.1458
- Expected sources: sample_paper_notes.md
- Retrieved sources: sample_train.log, sample_train.log, sample_train.log
- Missing keywords: source, boundary-aware, retrieved context
- Failure reason: Expected source was not retrieved in top-k.

## q020 - Tool Calling 在这个项目中适合把哪些任务交给确定性工具？

- Score: 0.5
- Expected sources: sample_train.log, sample_paper_notes.md
- Retrieved sources: sample_train.log, sample_train.log, sample_paper_notes.md
- Missing keywords: training logs, class-wise IoU, F1-score, Markdown report, plots
- Failure reason: Retrieved context or answer missed many expected keywords.

