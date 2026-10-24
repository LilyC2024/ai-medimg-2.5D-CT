# Lung detector model card

[Overview](../../README.md) · [Architecture](architecture.md) · [Evidence](../../EVALUATION.md)

The pretrained architecture/weights remain unchanged; the research extension adds explicit excerpt-only inference and source-mapped public evidence.

| Item | Description |
| --- | --- |
| Task | Candidate pulmonary-nodule boxes on supported volumetric CT |
| Backbone | MONAI 3D ResNet50 RetinaNet, FPN and three anchor shapes |
| Weights | Official LUNA16 bundle; fixed revision in detection.py |
| Adaptation | Offline artifact loading, bounded sliding-window inference, source-grid mapping and human review |
| Outputs | Candidate boxes/scores, box spans and optional reviewer-selected calipers |
| Intended use | Local educational/research inspection with expert review |
| Not implemented | Cancer diagnosis, all-abnormality detection, segmentation, tracking or management recommendations |
| Executed evidence | Official weights on generated phantom and a declared real LIDC-IDRI ROI; non-ML fixtures remain separate |
| Clinical/external patient evaluation | No independent clinical evaluation; annotation-selected ROI is a localization smoke only |
| CUDA/new-detector NPU | Actual execution not demonstrated on the recorded CPU-only host |

Default .15 score threshold is not clinically validated. Upstream metrics belong
to their original cohort/protocol; the changed inference recipe needs independent
assessment. Audit pretrained training overlap. Small/subsolid lesions, acquisition
changes and artifacts require specific evaluation. No candidates never rules out
nodules/cancer. Detector score is not malignancy risk.

The fixture finder and legacy four-class 2.5D U-Net are different components/tasks.
Neither phantom success nor legacy Dice/NPU timing demonstrates this detector's
clinical performance. LOVISA accepts reviewed synthetic or separately labelled public-research excerpts in fictional cases into its clinical summary; this is not a diagnosis.

The real ROI is 32×96×96 at source origin (168,313,300), selected from an official reader contour before inference. Only that region was analysed; the rest of the scan was not. Inference-region bounds are exported separately from full-source metadata. [Commands and terms](public-demo.md).

## Engineering audit versus model validation

The 24 October code review tightened archive cleanup, numeric source/target checks
and workspace creation. It did not alter architecture, weights, threshold, model
registration or the recorded ROI result. New regression counts measure software
behavior only; they cannot be added to model accuracy evidence. [Audit](../review.md).
