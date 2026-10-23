# CT project documentation

[Project overview](../README.md)

The active project is the **Lung CT Research Assistant**. Its companion **LOVISA**
organizes history and prepares the reviewed clinical report. Earlier “MHCRA”
references identify LOVISA's former name or stable integration interfaces.

| Your goal | Read |
| --- | --- |
| Understand model/coordinates/trust | [Architecture](lung/architecture.md) |
| Choose supported CT and review data permission | [Data](lung/data.md) |
| Inspect candidates, measure and complete CT review | [Review](lung/review.md) |
| Send synthetic evidence to LOVISA | [Integration](lung/mhcra.md) |
| Install CPU/CUDA, run Docker or troubleshoot | [Deployment](lung/deployment.md) |
| Prepare labels, launch training or evaluate detection | [Training](lung/training.md) |
| Find functions and folders | [Code reference](lung/code-reference.md) |
| Understand intended use and limitations | [Model card](lung/model-card.md) / [Scope](regulatory_scope.md) |
| Reproduce software checks and inspect outcomes | [Validation](validation.md) / [Evaluation](../EVALUATION.md) |
| Understand changes and portfolio claims | [Release](lung/release.md) |

Legacy 2.5D work has a separate [pipeline guide](legacy-pipeline.md),
[architecture](architecture.md), [model card](model_card.md),
[reproduction commands](reproducibility.md) and [dated record](release_notes.md).
Its pseudo-label metrics and NPU timings are not lung-nodule evidence.
