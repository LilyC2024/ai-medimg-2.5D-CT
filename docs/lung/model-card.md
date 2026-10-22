# Model card

Version 0.9.0. [Overview](../../README.md) · [Evaluation](../../EVALUATION.md)

| Item | Description |
| --- | --- |
| Task | Candidate pulmonary nodule boxes on supported volumetric CT |
| Backbone | MONAI 3D ResNet50 RetinaNet, FPN, three anchor shapes |
| Weights | Official LUNA16 bundle; revision pinned in detection.py |
| Adaptation | Offline loading, source mapping, review and evidence-linked report |
| Intended use | Educational local research with expert inspection |
| Output | Boxes, scores, box spans, optional reviewer-placed calipers |
| Not implemented | Malignancy diagnosis, all-abnormality detection, segmentation, tracking, management |
| Local data | Generated phantom; no new patient-data accuracy evaluation |
| Executed inference | Official weights on generated phantom; smoke JSON records details |
| Clinical sensitivity/external validation | Unknown/not performed |
| Accelerators | No CUDA/OpenVINO device available in development host |

Upstream metrics belong to their own protocol/cohort and are not application
accuracy. Audit training overlap. Default threshold .15 is not clinically validated.
Small/subsolid nodules, motion, unusual acquisitions and domain shifts require
specific evaluation. No candidates does not exclude cancer or establish normality.

The non-ML fixture finder is a different test component, with a sentinel score.
The legacy four-class 2.5D U-Net is also a different task; its Dice/NPU timings do
not describe this detector. No expert clinical validation is claimed.
