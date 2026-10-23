# Lung project release and engineering record

[Overview](../../README.md) · [Evaluation](../../EVALUATION.md)

## Documentation update — LOVISA naming

The history application is now **LOVISA — Medical History & Clinical Reasoning
Assistant**. Rewritten guides distinguish CT image analysis from LOVISA history/
reasoning/report review, explain the reused pictures and separate current tools
from legacy evidence. Existing repository, package and `mhcra-*` interfaces stay
stable; no detector/schema/weight change is part of this documentation update.

## v0.10.0 — implemented nodule interoperability

Added nodule-v2 exchange with bounded HU, every-slice previews, typed review/status,
hash manifest and canonical report. ML-free contracts/NumPy rendering are shared
with the LOVISA consumer and checked for drift. The dedicated bridge creates
pending fixture/pretrained input without issuing approval. Default standalone
export remains review-gated. Oversized exports fail rather than crop silently.

LOVISA added authenticated candidate/caliper review and a source-linked appendix
covered by separate final clinical approval. Legacy tissue-mask support remains.
[Compatibility/migration](mhcra.md) · [Exact test/run evidence](../../EVALUATION.md).

## v0.9.0 — lung research workflow

Introduced pinned MONAI 3D RetinaNet loading, offline tensor-only weights, explicit
CPU/CUDA, RAS/LPS source-grid mapping, generated chest phantom, fixture finder,
reviewable calipers and deterministic research reports. Added separate permitted
public-research input, patient/hash-separated manifests, upstream CUDA training
launcher, engineering FROC, device inventory and latency scripts.

Windows UTF-8 fixes and full pytest collection replaced incomplete unittest-only
checks. Removed obsolete pseudo-label report generation/redundant index aliases;
retained the DICOM loader, U-Net/ONNX/Intel tools and legacy bridge for reproducibility.
Their metrics remain historical. [Legacy changes](../release_notes.md).

## Engineering and portfolio descriptions

Supported description: “Built a local CT research assistant around pretrained
MONAI 3D RetinaNet with source-preserving annotations, manual physical measurements,
review-gated evidence-linked reporting and a validated synthetic connection to
LOVISA's local history workflow.”

A separate claim may describe the measured historical 2.5D ONNX/OpenVINO Intel NPU
experiment, with its original task/hardware/evidence. Do not claim clinically
validated cancer detection, new-model NPU acceleration, upstream benchmark
accuracy, a newly trained model or reduced clinician reading time.

AI coding assistance supported implementation, tests and documentation. Runtime
CT has no LLM agents. LOVISA's sequential specialist roles are distinct from
coding review subagents; neither software review nor scripted approval is clinical
verification. [LOVISA architecture](https://github.com/LilyC2024/Medical-AI/blob/main/docs/ARCHITECTURE.md).
