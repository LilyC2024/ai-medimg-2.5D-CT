# CT documentation

[Project overview](../README.md) · [LOVISA](https://github.com/LilyC2024/Medical-AI)

The current product is a lung-nodule research assistant. The older 2.5D
segmentation/deployment exercise is retained as a distinct engineering track.

| Task | Guide |
| --- | --- |
| Install environments and launch the local UI | [Setup](setup.md) |
| Load sources, inspect candidates and place calipers | [Review](lung/review.md) |
| Understand arrays, source geometry, model and trust | [Architecture](lung/architecture.md) |
| Find folders, functions and CLI entry points | [Code reference](lung/code-reference.md) |
| Prepare permitted volumes and patient-separated experiments | [Data](lung/data.md) / [Training](lung/training.md) |
| Select CPU/CUDA and understand NPU limitations | [Deployment](lung/deployment.md) |
| Inspect detector scope and limitations | [Model card](lung/model-card.md) |
| Transfer synthetic/public evidence to LOVISA | [Integration](lung/mhcra.md) |
| Reproduce the bounded real CT demonstration | [Public demo](lung/public-demo.md) |
| Run checks and inspect fixes | [Validation](validation.md) / [Expert review](review.md) |
| Inspect actual software/model evidence | [Evaluation](../EVALUATION.md) |
| Reproduce the historical 2.5D path | [Legacy guide](legacy-pipeline.md) / [Reproducibility](reproducibility.md) |

[Scope](regulatory_scope.md) · [Security](../SECURITY.md) ·
[Contribution workflow](../CONTRIBUTING.md) · [Phases](../PLAN.md).
The documentation distinguishes scripted tests, real model execution and unexecuted
hardware/training work. None constitutes clinical certification.
