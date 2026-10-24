# Expert source review — 24 October 2026

[Overview](../README.md) · [Checks](validation.md) · [Actual evidence](../EVALUATION.md)

A CT specialist reviewed source loading, geometry, training preparation, model and
review workspaces, exchange boundaries, legacy API uploads and tests. The primary
agent checked documentation and producer/consumer compatibility. These are code
reviews, not clinician or model-performance validation.

| P2 finding | Reproduction and repair |
| --- | --- |
| Temporary upload cleanup trusted member folder names | A nested `ct25d_dicom_*` folder could confuse cleanup. The API now explicitly owns the extraction root and removes the entire upload lifetime. |
| Duplicate/encrypted ZIPs had ambiguous failure behavior | Duplicate normalized paths are rejected before extraction; encrypted input returns a validation error instead of an unhandled runtime exception. |
| Fractional legacy class labels were truncated | Labels are checked for finite, real, integer class IDs in range before casting. Invalid targets fail instead of changing their meaning. |
| Research preflight accepted invalid HU | Source arrays are checked for finite real numeric voxels in addition to hash, affine and spacing checks. |
| Invalid workspace input reserved output paths | Shape/finite/real/float32-range checks now precede directory creation. Corrected input can retry the same previously uncreated destination. |

Repairs are in `deploy/app.py`, `deploy/inference_runtime.py`,
`src/data/ct25d_dataset.py`, `src/lung_nodule/research.py` and
`src/lung_nodule/workspace.py`. Eighteen targeted regressions accompany them.
The full runtime suite passed before the documentation phase; final combined
counts and actual pretrained smokes are recorded in [Evaluation](../EVALUATION.md).

No shared wire schema, dependency, installed weight, dataset, actual review or
clinical hypothesis changed. Local administrators and data-permission declarations
remain trusted. GPU training, new-detector NPU inference and independent clinical
performance are not established by this review.

These were AI-assisted source reviews, not independent human clinical or security
audits. Runtime specialist roles are separate from development review agents.
See [branch integration decisions](BRANCH_REVIEW.md).
