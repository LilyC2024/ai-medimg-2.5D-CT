# Lung detector model card

[Overview](../../README.md) · [Architecture](architecture.md) · [Evidence](../../EVALUATION.md)

Version 0.10.0. This version added exchange interoperability; detector unchanged.

| Item | Description |
| --- | --- |
| Task | Candidate pulmonary-nodule boxes on supported volumetric CT |
| Backbone | MONAI 3D ResNet50 RetinaNet, FPN and three anchor shapes |
| Weights | Official LUNA16 bundle; fixed revision in detection.py |
| Adaptation | Offline artifact loading, bounded sliding-window inference, source-grid mapping and human review |
| Outputs | Candidate boxes/scores, box spans and optional reviewer-selected calipers |
| Intended use | Local educational/research inspection with expert review |
| Not implemented | Cancer diagnosis, all-abnormality detection, segmentation, tracking or management recommendations |
| Executed evidence | Official weights on generated phantom; separate non-ML fixture and software tests |
| Clinical/external patient evaluation | Not performed; sensitivity and clinical utility unknown |
| CUDA/new-detector NPU | Actual execution not demonstrated on the recorded CPU-only host |

Default .15 score threshold is not clinically validated. Upstream metrics belong
to their original cohort/protocol; the changed inference recipe needs independent
assessment. Audit pretrained training overlap. Small/subsolid lesions, acquisition
changes and artifacts require specific evaluation. No candidates never rules out
nodules/cancer. Detector score is not malignancy risk.

The fixture finder and legacy four-class 2.5D U-Net are different components/tasks.
Neither phantom success nor legacy Dice/NPU timing demonstrates this detector's
clinical performance. LOVISA accepts a reviewed synthetic study into its clinical summary; this is not a diagnosis.
