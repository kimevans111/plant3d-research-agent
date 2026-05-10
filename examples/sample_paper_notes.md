# Plant-GeoAT Notes for Tomato Point Cloud Segmentation

Plant-GeoAT is designed for 3D plant point cloud semantic segmentation where leaves, stems, and petioles have very different geometry but often touch or overlap in raw scans.

## Leaf-Stem Boundary Confusion

Leaf-stem boundary confusion happens when points near the petiole, main stem, and curled leaf margins share similar coordinates or local density. A plain point MLP may treat these points as a smooth mixed region, so thin stem points can be absorbed into the leaf class.

Plant-GeoAT mitigates this problem by using geometry-aware attention. The attention module emphasizes local surface variation, relative position, neighborhood topology, and direction-sensitive cues. This helps the network identify narrow cylindrical stem structures even when they are adjacent to broad leaf surfaces.

In our notes, Plant-GeoAT improves stem IoU because it aggregates features along structural continuity rather than only Euclidean proximity. Boundary-aware geometric aggregation can reduce false leaf predictions at junctions and makes the leaf-stem transition sharper in semantic maps.

## Experimental Interpretation

When mIoU improves but stem IoU remains low, the likely bottleneck is thin-structure recall rather than global segmentation quality. Useful diagnostics include class-wise IoU, F1-score, boundary region visualization, and confusion matrices around leaf-stem contact zones.

## Practical Suggestions

- Use class-balanced loss or focal loss when stem points are rare.
- Add rotation, jitter, and partial occlusion augmentation.
- Compare Plant-GeoAT with PointNet++, DGCNN, PointTransformerV3, PointVector, and PointLIBR.
- Report OA, mIoU, mAcc, Precision, Recall, F1-score, leaf IoU, stem IoU, RMSE, MAE, and R2 when phenotype regression is included.
