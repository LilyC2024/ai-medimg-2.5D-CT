# Historical tissue-pipeline release record

[Current release history](lung/release.md) · [Legacy overview](legacy-pipeline.md)

## v0.8.0 — 4 October 2026

The repaired head-region experiment replaced earlier inconsistent sprint-era
claims. Source/results remain recoverable at `457ddbf`; an old local checkpoint
is not the repaired deployment model.

| Area | Repaired behavior |
| --- | --- |
| Ingestion/HU | Validate one regular series; apply rescale once including compressed fallback and padding |
| Geometry | Preserve physical transforms and invert masks to the source grid |
| Dataset/training | Relative frozen manifests, stack-support isolation, patient grouping and reproducible epoch augmentation |
| Evaluation | Explicit nonempty splits, contiguous-volume postprocessing and global class statistics |
| Runtime | ONNX graph/parity gates bound to checkpoint/preprocessing; reusable CPU sessions |
| Intel | Actual full U-Net NPU-only execution with declared FP16 quality/latency evidence |
| Service/container | Bounded localhost API, artifact cleanup and hosted CPU container execution |
| Publication | MIT code license, numeric metadata allowlist and ignored patient/model artifacts |

The historical [verification JSON](../reports/verification.json) records 30 required
tests with no skips, separate fresh-environment/checkout reproduction and hosted
checks. [Measured outcomes](legacy-pipeline.md) include low pseudo-label agreement
and degradation after postprocessing; neither was hidden or turned into a clinical
claim. The source sample's acquisition/redistribution terms remain unresolved.

Key repair commits: `baf1111` (core), `d8dd992` (Windows memory handles), `5bbe71b`
(power/cache evidence), `dfde7b4` (runtime binding), `f963c49` (input validation),
`d2bc89f` (container), `3b25016` (evidence) and `c075888` (hosted verification).
Full chronology remains in Git history; no history rewrite or patient/model release
was performed.

## Synthetic history-workbench extension — 22 October 2026

Added deploy.mhcra_bridge, explicit synthetic patient/study identity, all-slice
previews and source-grid measurements. Tiny-model training and parity were tested;
the general research CLI/API remained separate. [Integration evidence](../reports/mhcra_integration.json).
The receiving app is now **LOVISA**. Current lung work and nodule-v2 interoperability
are documented in the [active release record](lung/release.md).
