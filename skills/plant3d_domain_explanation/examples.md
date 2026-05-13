# Plant3D Domain Explanation Examples

## 1. Boundary confusion

User: "解释 leaf-stem boundary confusion。"

Expected skill behavior:

- Explain that points near leaf/stem junctions can have ambiguous geometry or labels.
- Avoid claiming project-specific improvements without evidence.

## 2. Thin stem missing

User: "thin stem missing 是什么失败案例？"

Expected skill behavior:

- Explain that thin stem points may be sparse, occluded, or confused with nearby leaves.

## 3. mIoU and F1

User: "mIoU 与 F1 有什么区别？"

Expected skill behavior:

- Explain overlap-based and precision/recall-based perspectives.
- Mention class imbalance implications.

## 4. Low stem IoU

User: "为什么 stem IoU 低？"

Expected skill behavior:

- List likely factors such as thin structure, boundary confusion, imbalance, and annotation noise.
- Ask for or use metrics before making a run-specific claim.

## 5. Paper-style wording

User: "把实验结果转成论文式表达。"

Expected skill behavior:

- Use only metrics supplied by the user or parser.
- Mark missing values as unavailable.
