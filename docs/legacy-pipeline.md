# Retained 2.5D tissue-mask experiment

[Current lung project](../README.md) · [Legacy architecture](architecture.md) ·
[Reproduction](reproducibility.md) · [Evidence](validation.md)

This is the earlier head-region pseudo-label experiment. It remains useful for
DICOM geometry, training/evaluation, ONNX parity and measured Intel NPU practice.
It is a different task from lung-nodule detection. Its masks, Dice and per-stack
latencies do not measure the current detector's clinical performance.

## What the legacy pipeline does

DICOM → rescale once → physical resampling/head crop → heuristic four-class teacher
→ neighboring-slice stacks → small U-Net → source-grid mask. Class IDs are
background, brain-like candidate, broad bone-like candidate and overlap. These are
heuristic labels, not validated anatomy, lesions or clinical ground truth.

| Component | Purpose |
| --- | --- |
| dicom_loader.py / preprocessing.py | HU, padding, regular geometry, physical crop/resampling and inverse restoration |
| src/baselines | Versioned classical pseudo-label teacher |
| src/data | Relative manifests, 2.5D stack support and frozen split checks |
| src/models | Compact four-class U-Net, loss and metrics |
| scripts/train.py / infer.py | Validation-selected training and explicit held-out evaluation |
| export_verified.py / deploy.cli_infer | Bound checkpoint/ONNX contracts, parity and source-grid CPU output |
| benchmark_intel.py | Identical-input CPU/NPU comparisons and execution-device evidence |
| deploy.app | Experimental bounded localhost API, not a nodule API |
| deploy.mhcra_bridge | Retained synthetic tissue-mask input for LOVISA |

## Reproduce with generated pixels

Use the current Python 3.12 setup with `.[ml,dev]`. Run from the repository root:

```bash
.venv/bin/python scripts/generate_fixture.py artifacts/legacy/series
.venv/bin/python scripts/prepare_case.py --series-dir artifacts/legacy/series --output-dir artifacts/legacy/processed
.venv/bin/python scripts/train.py --index-path artifacts/legacy/processed/index.csv --output-dir artifacts/legacy/train --model-dir artifacts/legacy/models --epochs 1 --image-size 32,32 --base-channels 2
.venv/bin/python scripts/export_verified.py --checkpoint artifacts/legacy/models/best.pt --index artifacts/legacy/processed/index.csv --onnx artifacts/legacy/model.onnx --output artifacts/legacy/runtime
.venv/bin/python -m deploy.cli_infer --series-dir artifacts/legacy/series --checkpoint artifacts/legacy/models/best.pt --onnx-path artifacts/legacy/model.onnx --output-dir artifacts/legacy/prediction --output-formats mask
```

The tiny demonstration exercises software flow, not anatomy. Source mask shape
is 20×48×48. Use `python -m pytest -q` for the full current suite; unittest discovery
alone does not collect all active nodule tests. [Additional commands](reproducibility.md).

## Historical measured results

| Measurement | Recorded result | Evidence |
| --- | --- | --- |
| Raw / postprocessed foreground macro Dice | 0.30325 / 0.14451 against pseudo labels | [Evaluation](../reports/evaluation.json) |
| CPU ONNX maximum difference / mask agreement | 4.17e-7 / 100% | [Parity](../reports/onnx_parity.json) |
| Warm PyTorch / ORT / OpenVINO CPU p50 | 69.08 / 50.51 / 42.37 ms per stack | [Intel benchmark](../reports/intel_benchmark.json) |
| Warm Intel NPU p50 / p95 | 4.94 / 6.21 ms per stack | [Intel benchmark](../reports/intel_benchmark.json) |
| NPU mask agreement / absolute Dice drop | 99.9943% / 0.000080 on model grid | [Intel benchmark](../reports/intel_benchmark.json) |

The baseline used one local 34-source-slice series and a same-series split (18 train,
4 validation, 4 test, 4 buffer centers). It does not establish unseen-patient
performance. Teacher quality is weak; postprocessing worsened agreement. Historical
sample source/redistribution terms remain unresolved, so no real-data download or
artifact release is promised. [Data/privacy](data.md).

NPU timing used a fixed 256×256 model grid, identical inputs, three warmups and
30 repeats on the recorded Intel hardware. It is not DICOM-to-report latency.
Application caches were disabled; driver caches were not reset. Peak memory is
cumulative process memory, not device RAM. [Runtime detail](reproducibility.md).

## LOVISA compatibility

The legacy `mhcra-imaging-v1` bridge is still supported by **LOVISA** (formerly
MHCRA AI). It is separate from current `mhcra-lung-nodules-v2`. The two formats must
never be interchanged by renaming. [Legacy bridge](mhcra-workbench.md) ·
[Current nodule integration](lung/mhcra.md).

## Maintained behavior after expert review

This path remains available for reproducibility and deployment experience. The
review repaired API extraction ownership, encrypted/duplicate upload rejection
and source-label validation before casting. Its clinical scope and recorded
teacher/NPU metrics are unchanged. Current lung work uses a different model,
protocol and evidence stream. [Repairs](review.md) · [Function reference](lung/code-reference.md).

The historical slice counts refer to different stages: **34 source slices → 30
cropped/processed slices → 18 training / 4 validation / 4 test / 4 buffer centers**.
The 30-center split is not a claim that the original source had only 30 slices.
