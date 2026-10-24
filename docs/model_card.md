# Legacy tissue-mask model card

[Active lung model card](lung/model-card.md) · [Legacy architecture](architecture.md)

| Item | Historical experiment |
| --- | --- |
| Task | Agreement with four heuristic head-region pseudo classes |
| Model | Compact 2.5D U-Net; 482,788 parameters, base width 16, 256×256 |
| Training | One CT series; 18 train, 4 validation, 4 test and 4 buffer centers; eight CPU epochs |
| Selection | Validation foreground macro Dice; seed 13, Adam and CE/Dice loss |
| Raw / postprocessed test agreement | ~0.303 / ~0.145 foreground macro Dice against the teacher |
| Deployment evidence | Verified ONNX CPU and measured full-model Intel NPU on a fixed model grid |
| Missing evidence | Expert labels, patient/site external validation, lesion diagnosis and clinical utility |

Broad teacher classes include nonbone tissue, class 1 is rare and overlap dominates
central regions. Teacher agreement cannot establish medical accuracy or superiority
to that teacher. Uncertainty is model behavior, not clinical confidence.

The separate LOVISA legacy fixture uses a tiny 32×32/base-width-4 model trained
for 12 epochs; it is not the measured 256×256 baseline. Its tissue-mask output is
not a nodule detector. [Bridge](mhcra-workbench.md).

An AI coding assistant implemented/reviewed software and tests. No independent
expert clinical approval is claimed. Source sample permissions remain unresolved;
code MIT terms grant no patient-data rights. Historical checkpoints/metrics are
identified by their own records, not current lung-project performance.

The 24 October source repairs affect input integrity and cleanup only. They do
not retrain this historical model, alter its original teacher metrics or validate
NPU execution for the newer RetinaNet detector. [Audit](review.md).
