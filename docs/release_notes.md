# 0.8.0 changes — 4 October 2026

This dated record covers the repairs promoted to `main` on 4 October 2026 (Europe/Stockholm). Version 0.8.0 is a research prototype, with no clinical or CE claim. The historical baseline remains recoverable at `457ddbf`; its checkpoint and metrics are superseded for current deployment.

## Implementation updates

| Area | Changed behavior |
| --- | --- |
| DICOM ingestion | Validate single-frame monochrome CT, required decode tags, series membership, dimensions and regular geometry. Sort by projected physical position; reject duplicates, nonuniform spacing, localizers, mixed series, unsupported multiframe and gantry tilt. |
| HU and padding | Apply rescale exactly once on pydicom and SimpleITK paths, including compressed input. Exclude stored pixel padding from relevant statistics and ROI logic. Independent real JPEG decoding agreed with SimpleITK. |
| Physical geometry | Preserve origin/direction/spacing; save resampling/crop transforms; restore labels to the original CT grid with nearest-neighbor interpolation. NPZ and NIfTI source geometry agree. |
| Data and pseudo labels | Generate images, four heuristic labels, validated relative index references, frozen splits and checksums through one preparation path. Record thresholds, morphology and preprocessing contracts; reject malformed rows and fractional slice coordinates. |
| Split and training | Use disjoint complete neighboring-slice support, patient grouping, discarded boundary centers and no held-out fallback. Add epoch-varying reproducible synchronized augmentation, validated configuration and safely loaded traceable checkpoints. Retrain the corrected eight-epoch CPU baseline. |
| Evaluation and calibration | Evaluate explicit splits in slice order, apply postprocessing to contiguous volumes and aggregate class metrics globally. Verify batch invariance. Report rare-class failures, postprocessing degradation and historical NLL worsening; primary temperature remains identity. |
| ONNX and runtime | Check the graph, export declared spatial contracts with dynamic CPU batch, verify representative/boundary inputs and fail parity errors. Bind the graph to checkpoint hashes and exact preprocessing contracts. Reuse runtime sessions and export source-grid masks. |
| Intel validation | Execute the full U-Net on the actual Intel NPU, require explicit NPU-only device evidence and compare FP16 quality with identical FP32 CPU inputs. Record compilation/first inference, warm latency, precision, power, driver, thread settings and cumulative process peak memory. |
| Service and container | Keep CLI primary and API experimental. Initialize once, report readiness correctly, bound uploads/dimensions, reject unsafe archives and ambiguous series, clean temporary data and return downloadable mask/metadata. Build and exercise the CPU Docker image in Linux CI. |
| Packaging and repository | Define Python 3.12 dependencies in pyproject, remove unused MONAI and production path hacks, document CPU wheels/constraints, add user-selected MIT code license and sanitize public metadata. Consolidate historical docs and redundant implementations; retain local datasets/checkpoints while removing their Git tracking. |
| Documentation | Rewrite README, data, architecture, reproduction, validation, model card and regulatory scope around verified behavior. Retire CT_Project_TODO.md; retain all unresolved requirements below and keep the original backlog in Git history. |

## Verification and measured results

[Machine-readable verification](../reports/verification.json) records the exact tested implementation and [successful Windows/Linux CI](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/37233373549). The CI result covers commit `3b25016`; subsequent documentation commits do not change runtime behavior.

- All 30 required tests pass without skips, and lint passes. Tests cover geometry, rescale-once, compressed input, split support, malformed input, runtime binding, metrics, CLI/API behavior and temporary cleanup.
- A separate checkout and new Python environment completed synthetic generation, preparation, training, export and CPU CLI inference. Real-data evaluation also passed under a relocated data root and different working directory.
- Evaluation masks agree across batch sizes 1/2/3; source-grid CLI masks agree across batch sizes 1/3. NPZ/NIfTI geometry and label content agree.

| Measurement | Recorded result | Evidence |
| --- | --- | --- |
| Corrected demonstration partition | 18 train, 4 validation, 4 test, 4 buffer centers; zero direct stack-support overlap | [Data manifest](../reports/data_manifest.json) |
| Raw / postprocessed test foreground macro Dice | 0.30325 / 0.14451 against pseudo labels | [Evaluation](../reports/evaluation.json) |
| ONNX CPU parity | Maximum probability difference 4.17e-7; 100% mask agreement | [CPU parity](../reports/onnx_parity.json) |
| Warm stack inference p50 | PyTorch CPU 69.08 ms; ONNX Runtime CPU 50.51 ms; OpenVINO CPU 42.37 ms; NPU 4.94 ms | [Intel benchmark](../reports/intel_benchmark.json) |
| FP16 NPU comparison | 99.9943% mask agreement; foreground Dice drop 0.000080 on the 256x256 model grid | [Intel benchmark](../reports/intel_benchmark.json) |
| Hosted CPU container | Image built and synthetic source-grid inference passed on Linux | [CI evidence](../reports/verification.json) |

Warm runtime timing is per 2.5D stack, with three warmups and 30 repeated runs; it is not DICOM-to-mask latency. Runtime quality uses model-grid metrics, while the primary evaluation uses the processed grid. FP16 NPU passes its declared Dice gate and exceeds the tighter FP32 CPU probability gate. Application caches were disabled; driver caches were not reset. Process peak memory is cumulative, not device RAM. These are machine-specific engineering measurements.

## Commit record

| Commit | Update |
| --- | --- |
| `baf1111` | Core CT, split, training/evaluation, CPU deployment, packaging, documentation and license repairs |
| `d8dd992` | Correct Windows memory instrumentation handles |
| `5bbe71b` | Record AC power and distinguish application/driver caching |
| `dfde7b4` | Bind deployment artifacts to checkpoint/preprocessing contracts |
| `f963c49` | Reject malformed decoding tags and noninteger index coordinates |
| `d2bc89f` | Build and exercise the CPU container in Linux CI |
| `3b25016` | Curate measured evidence and the completed/open task audit |
| `c075888` | Record passing hosted Windows/Linux and Docker verification |

The final documentation commit retires the backlog and consolidates this dated record before promotion to `main`. No Git history is rewritten and no data/model release assets or release tag are published.

## Remaining research and publication requirements

- Establish the real sample's source URL, acquisition terms, ownership and research/redistribution permissions. Original-file hashes, real overlays and trained model artifacts remain local pending review; a real-data download cannot currently be reproduced publicly.
- Review any prospective images separately for burned-in text, identifying anatomy and redistribution permission. Aliases and hashes are not full DICOM anonymization. Previously committed identifiers may need a separate disclosure/history assessment.
- Obtain clinician confirmation of the proposed clinical task, permitted expert-annotated multi-patient data and an annotation quality protocol. Plan patient/site/scanner separation, external evaluation and matched model comparisons.
- Assess clinical evaluation, risk management, software lifecycle, usability, cybersecurity and post-market obligations before a clinical product claim. Official scope references are in [regulatory scope](regulatory_scope.md).
- Treat low pseudo-label agreement, rare-class failure and worse postprocessing as observed limitations. There is no independent clinical accuracy or calibration-generalization evidence.
- Exact shell commands from the original Windows session were unavailable; [baseline evidence](../reports/baseline.json) records this without inventing history. Local Docker is unavailable; its verification was performed by hosted Linux CI. Namespace migration to `src/ct25d` is deferred because the tested installed modules already work.

A release tag and public patient/model asset distribution remain withheld until acquisition and publication requirements are resolved. The code license is MIT and grants no rights to source data or third-party assets.
