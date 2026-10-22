# v0.9.0 release and engineering record

22 October 2026. [Overview](../../README.md) · [Actual checks](../../EVALUATION.md)

## Changes

- Reframed the active deliverable from heuristic tissue segmentation to local lung
  nodule candidate detection and human-reviewed research summaries.
- Added pinned official MONAI 3D RetinaNet loading, strict tensor-state checks,
  explicit CPU/CUDA devices and verified offline artifacts.
- Added source geometry/identity, candidate, provenance, caliper and review schemas.
  Source-grid box mapping transforms all eight corners through RAS/LPS affines.
- Added a generated chest-like phantom and explicitly non-ML fixture finder.
  Added separately executed real pretrained smoke; no newly trained model claimed.
- Added source/overlay viewer, accept/reject/uncertain decisions, caliper previews,
  source-hash evidence and approval-bound deterministic report export.
- Added approved public research input separated from MHCRA synthetic records,
  resampled HU NIfTI preparation, patient/hash-separated manifest validation,
  upstream CUDA training launch and transparent engineering FROC scoring.
- Added actual-device inventory and full-pipeline latency scripts. Kept historical
  OpenVINO/NPU evidence separate from unexecuted new-detector acceleration.
- Split the oversized root README into a short overview and linked subject guides;
  added an API/folder reference and reproducible generated illustration.
- Fixed Windows default-encoding failures with explicit UTF-8 text IO, Unicode
  regressions, consistent formatting and independent platform CI execution.

## Removed and retained

Removed scripts/report.py: obsolete Day 6 pseudo-label report generator whose
anatomical naming and input filenames no longer represented the active workflow.
Removed scripts/make_index.py: redundant compatibility alias for prepare_case.py.
Updated scripts/check.py and CI to pytest so the new tests cannot be silently
omitted by unittest discovery. The full old README moved to legacy-pipeline.md
with corrected relative links and explicit historical labeling.

Retained the shared loader, geometry tests, old 2.5D training/export, ONNX parity,
OpenVINO benchmark and MHCRA v1 bridge because they have reproducibility or
compatibility value. Removing them would break existing MHCRA consumers and erase
useful engineering evidence. Historical report hashes remain historical.

## CV and interview descriptions

Defensible: “Built a local CT research assistant around pretrained MONAI 3D
RetinaNet, with geometry-preserving candidate overlays, source-bound manual
measurements and human-reviewed evidence-linked reports; added patient-separated
dataset validation and CPU/CUDA deployment workflows.”

Also defensible with the historical context: “Implemented and measured a separate
2.5D ONNX/OpenVINO deployment experiment on an Intel NPU, checking numeric/label
parity and explicit device execution.” Cite the old task, hardware and evidence.

Do not claim to have trained a clinically validated cancer detector, demonstrated
new-model NPU acceleration, achieved upstream benchmark accuracy, or reduced
doctors' reading time. No clinical reader study or new patient-data evaluation
exists. Identify pretrained work and upstream contributions explicitly.

Development used an AI coding assistant for implementation, test generation and
documentation. This release did not run autonomous medical agents or independent
human clinical review. The companion MHCRA's LangGraph specialists are separate
runtime components, described in [integration](mhcra.md).
