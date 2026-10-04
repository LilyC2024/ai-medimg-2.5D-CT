# CT 2.5D research prototype

A reproducible research pipeline for **CT DICOM ingestion, geometry-preserving preprocessing, classical pseudo-label generation, compact 2.5D U-Net training, evaluation, and verified CPU/Intel NPU inference**.

**Current version: 0.8.0.** The project is intended for software engineers, imaging researchers and reviewers studying an end-to-end medical-imaging implementation. Its present task is agreement with heuristic head-region labels. It does not diagnose lesions, establish anatomical ground truth, or demonstrate clinical accuracy.

A clean checkout includes source code, synthetic fixture generation, tests, configurations and sanitized evidence. **Real DICOM, derived patient images, trained checkpoints and ONNX models are not bundled.** Start with the synthetic workflow below; real-data reproduction requires a permitted input series and training your own model.

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Pipeline and functions](#pipeline-and-functions)
- [Input and output contracts](#input-and-output-contracts)
- [Model, labels and evaluation](#model-labels-and-evaluation)
- [Installation](#installation)
- [Synthetic end-to-end quickstart](#synthetic-end-to-end-quickstart)
- [Running with real CT data](#running-with-real-ct-data)
- [Deployment interfaces](#deployment-interfaces)
- [Intel NPU benchmarking](#intel-npu-benchmarking)
- [Recorded results](#recorded-results)
- [Repository structure](#repository-structure)
- [Testing and reproducibility](#testing-and-reproducibility)
- [Changes from previous versions](#changes-from-previous-versions)
- [Limitations and research requirements](#limitations-and-research-requirements)
- [Troubleshooting](#troubleshooting)
- [Documentation and license](#documentation-and-license)

## Purpose and scope

The aim is to make every stage of a small CT segmentation experiment inspectable: how stored pixels become HU, how physical geometry survives preprocessing, how neighboring slices are partitioned, how a model is selected, and whether exported runtimes reproduce its predictions.

The repository supports three practical uses:

1. **Software verification:** generate synthetic DICOM and exercise ingestion, preparation, training, export and deployment without external data.
2. **Research experiments:** provide an authorized head CT series, generate versioned heuristic targets, train the compact baseline, and inspect its agreement and failure cases.
3. **Runtime comparison:** compare PyTorch CPU, ONNX Runtime CPU, OpenVINO CPU and an actual Intel NPU on identical prepared tensors with declared numerical and quality gates.

The validated deployment interface is the CPU CLI. A localhost API is experimental. Intel NPU execution is a separately measured Windows hardware path. Clinical decision support, expert anatomical segmentation, multi-patient generalization and production service operation are outside the current demonstrated scope.

## Pipeline and functions

```text
CT DICOM series
  -> validate tags, decode pixels, sort by physical position
  -> apply modality rescale once and handle pixel padding
  -> resample in physical coordinates and crop head ROI
  -> clip HU and normalize intensities
  -> generate classical candidates and four pseudo classes
  -> freeze relative-path index, split support and checksums
  -> build ordered three-slice stacks and train a compact U-Net
  -> evaluate the requested split and record raw/postprocessed metrics
  -> export and validate a checkpoint-bound ONNX graph
  -> CPU inference or separate Intel CPU/NPU benchmark
  -> restore labels to the original CT grid and save geometry
```

| Function | Main implementation | Behavior |
| --- | --- | --- |
| DICOM loading | [dicom_loader.py](src/dicom_loader.py) | Validates supported CT, orders slices using physical coordinates, decodes compressed input with supported backends, and avoids double rescale. |
| Preprocessing | [preprocessing.py](src/preprocessing.py) | Resamples voxel centers, detects/crops a head ROI, normalizes intensities and records inverse geometry. |
| Pseudo labels | [classical_seg.py](src/baselines/classical_seg.py) | Combines heuristic brain-like and broad bone candidates, morphology and component filters. |
| Case preparation | [prepare_case.py](scripts/prepare_case.py) | Writes aligned volumes/labels, validated relative index references, frozen splits, configuration and checksums. |
| Dataset and training | [ct25d_dataset.py](src/data/ct25d_dataset.py), [train.py](scripts/train.py) | Builds three-channel stacks, enforces split contracts, applies synchronized augmentation and saves a traceable selected checkpoint. |
| Evaluation | [infer.py](scripts/infer.py), [evaluation.py](src/evaluation.py) | Computes split-specific global metrics and applies postprocessing to ordered contiguous runs. |
| Export and deployment | [export_verified.py](scripts/export_verified.py), [inference_runtime.py](deploy/inference_runtime.py) | Checks ONNX parity and artifact binding, reuses sessions, restores predictions and writes reports. |
| Optional analysis | [inspect_series.py](scripts/inspect_series.py), [report.py](scripts/report.py) | Produces local ingestion inspection artifacts and an evaluation report/montage from existing outputs. |

The old `preprocess_series.py`, `classical_baseline.py` and `make_index.py` entry points are compatibility wrappers around unified case preparation. Use `prepare_case.py` for new runs; historical command options are not a separate supported pipeline.

## Input and output contracts

### Supported CT input

Provide one directory containing one regular **single-frame monochrome CT DICOM series**. Required metadata includes consistent dimensions, `ImagePositionPatient`, `ImageOrientationPatient`, `PixelSpacing`, rescale slope/intercept and pixel-decoding tags. Regular axial and oblique geometry are supported. Slices are sorted by projection onto the orientation-derived slice normal, rather than by filename.

The loader rejects mixed series, localizers, multiframe CT, duplicate positions, nonuniform slice spacing, inconsistent orientation, missing required tags and gantry tilt/in-plane displacement. Limits are 512 slices, 1024 pixels per dimension and 64 Mi voxels. Compressed decoding depends on installed codecs or the rescale-aware SimpleITK/GDCM fallback; optional JPEG codecs are available through the `codecs` extra.

Array order is **z, y, x**; physical coordinates use DICOM LPS. Default preprocessing uses 1 mm in-plane spacing, retains coarse z spacing, clips HU to [-1000, 1000], and normalizes to [0, 1]. Keeping a 5 mm source z spacing avoids presenting interpolated slices as additional anatomical information. Crop bounds, physical origin, direction and forward/inverse mappings are saved. See [the geometry contract](docs/architecture.md).

### Generated artifacts

| Stage | Typical artifacts | Purpose |
| --- | --- | --- |
| Preparation | `volume.npz`, `labels.npz`, `index.csv`, `index.sha256`, `manifest.json`, `technical.json` | Aligned training data, frozen relative references, transforms, preprocessing/teacher parameters and quality checks. |
| Local source identity | `source_checksums.local.json` | Ordinal source-file hashes; retained locally pending publication permission. |
| Training | `best.pt`, `day5_train_report.json`, curves and calibration report | Selected model, architecture/data/config provenance and train/validation history. |
| Evaluation | `day5_infer_report.json`, `day5_predictions.npz`, local overlays | Requested-split raw/postprocessed metrics, predictions and failure inspection. |
| Verified export | `model.onnx`, `onnx_parity.json`, `runtime_inputs.npz` | Checkpoint-bound graph, parity evidence and identical benchmark tensors. |
| Deployment | `prediction_mask.npz` or NIfTI, preprocessing/runtime/parity reports | Source-grid uint8 class labels and restored physical geometry. |

Legacy `day5`/`day7` artifact names remain for compatibility; they do not imply different active implementations. Use explicit artifact directories in commands. Model/derived-image outputs are ignored local artifacts; selected small sanitized reports in [reports](reports/) document recorded runs.

## Model, labels and evaluation

### Four heuristic target classes

| ID | Meaning |
| --- | --- |
| 0 | Neither candidate; background for this teacher. |
| 1 | Brain-like candidate excluding the broad bone candidate. |
| 2 | Broad bone candidate excluding the brain-like candidate. |
| 3 | Overlap of the two candidates. |

These are **pseudo labels**, not expert annotations. In particular, the current bone candidate uses a -100 HU threshold and includes soft tissue. Brain-like candidates use an adaptive intensity-window and morphology/component procedure. The complete teacher parameters and selected candidate are recorded in each manifest. The class names describe heuristic behavior and should not be interpreted as verified anatomy.

### Compact 2.5D U-Net

For center slice z, channels are `[z-1, z, z+1]`, with boundary slices repeated at the ends. The network predicts the center slice. This adds limited through-plane context while retaining a small 2D network suited to CPU experimentation.

The baseline uses three input channels, four output classes, encoder widths 16/32/64, a 128-channel bottleneck and three decoder stages with concatenated skip connections. Double-convolution blocks use BatchNorm/ReLU; the output head produces four logits. It has **482,788 parameters**. Inputs resize to 256 x 256 with bilinear interpolation; labels resize by nearest neighbor.

[configs/baseline.json](configs/baseline.json) defines seed 13, Adam at 0.001, batch size 2, eight epochs and four CPU threads. Loss is 0.5 class-weighted cross entropy plus 0.5 foreground soft Dice. Synchronized flips/rotations and image-only intensity jitter vary reproducibly across epochs. Validation foreground macro Dice selects the checkpoint. CLI overrides allow smaller smoke runs. Primary calibration uses identity temperature; historical temperature scaling that worsened NLL is not presented as successful calibration.

### Split and metric semantics

Preparation makes a contiguous **single-series demonstration split**, excluding two centers at each boundary for radius-one stacks. Complete direct stack supports are disjoint, including boundary clamping. For multi-series manifests, all known series of one patient must stay in one split. The preparation CLI handles one case; it does not automate a clinical multi-patient study.

Training and evaluation require nonempty requested held-out splits and never substitute training data. Evaluation operates on one series per invocation, sorts slices physically, and postprocesses contiguous runs after concatenating batches. Per-class Dice/IoU use accumulated global voxel counts; the foreground summary is an unweighted mean. Classes empty in both target and prediction are null/excluded, with an all-empty foreground summary of zero.

Direct stack isolation does not make the sample independent: ROI decisions and teacher generation use the full series. The teacher's agreement with itself is tautological. Neither that comparison nor a same-series test establishes clinical accuracy or superiority to the teacher.

## Installation

Use **Python 3.12**. CPU workflows are tested on Windows and Linux. Intel NPU benchmarking additionally requires compatible Intel hardware, Windows drivers and OpenVINO. Docker is needed only for the container workflow.

The following PowerShell commands create an isolated environment and install the recorded CPU setup:

```powershell
git clone https://github.com/LilyC2024/ai-medimg-2.5D-CT.git
cd ai-medimg-2.5D-CT
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[ml,dev]" -c reports/windows-constraints.txt
```

Run subsequent commands from the repository root. Explicit virtual-environment executables avoid selecting a different Python installation. On Linux, create the environment with `python3.12 -m venv .venv`, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`, and install `.[ml,dev]` without the Windows-specific constraints, as CI does.

[pyproject.toml](pyproject.toml) is the dependency authority; `requirements.txt` forwards to it. Extras are `ml` for training/export/API, `dev` for lint/test support, `intel` for OpenVINO and `codecs` for additional JPEG decoding. Install optional extras only for the workflow you need:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[intel]"
.\.venv\Scripts\python.exe -m pip install -e ".[codecs]"
```

The [Windows constraints](reports/windows-constraints.txt) capture measured versions, rather than promising a universal cross-platform lock.

## Synthetic end-to-end quickstart

This workflow needs no patient files or downloaded pretrained model. It generates a small CT and trains a deliberately tiny one-epoch model to exercise software behavior. Its metrics have no anatomical interpretation.

```powershell
.\.venv\Scripts\python.exe scripts/check.py
.\.venv\Scripts\python.exe scripts/generate_fixture.py artifacts/synthetic/series
.\.venv\Scripts\python.exe scripts/prepare_case.py --series-dir artifacts/synthetic/series --output-dir artifacts/synthetic/processed
.\.venv\Scripts\python.exe scripts/train.py --index-path artifacts/synthetic/processed/index.csv --output-dir artifacts/synthetic/train --model-dir artifacts/synthetic/models --epochs 1 --image-size 32,32 --base-channels 2
.\.venv\Scripts\python.exe scripts/export_verified.py --checkpoint artifacts/synthetic/models/best.pt --index artifacts/synthetic/processed/index.csv --onnx artifacts/synthetic/model.onnx --output artifacts/synthetic/runtime
.\.venv\Scripts\python.exe deploy/cli_infer.py --series-dir artifacts/synthetic/series --checkpoint artifacts/synthetic/models/best.pt --onnx-path artifacts/synthetic/model.onnx --output-dir artifacts/synthetic/prediction --output-formats mask
```

Success means required tests execute and lint exits zero, preparation prints validated split counts, training saves `best.pt`, export reports `within_tolerance: true`, and CLI writes `prediction_mask.npz` on the original **20 x 48 x 48 source grid**. The synthetic model uses 32 x 32 input; it is distinct from the 256 x 256 research baseline.

## Running with real CT data

First obtain an authorized head CT series and review [data acquisition and privacy](docs/data.md). The local sample used for recorded evidence has no verified public source URL or redistribution terms. Place your permitted series in `data/dicom_series_01`, or replace that path below. Keep different runs in separate artifact directories.

```powershell
# Prepare normalized images, heuristic labels and a frozen demonstration split.
.\.venv\Scripts\python.exe scripts/prepare_case.py --series-dir data/dicom_series_01 --output-dir artifacts/real/processed

# Train using the recorded baseline configuration and validation selection.
.\.venv\Scripts\python.exe scripts/train.py --config configs/baseline.json --index-path artifacts/real/processed/index.csv --output-dir artifacts/real/train --model-dir artifacts/real/models

# Evaluate only the test split and save raw/postprocessed evidence.
.\.venv\Scripts\python.exe scripts/infer.py --index-path artifacts/real/processed/index.csv --checkpoint artifacts/real/models/best.pt --output-dir artifacts/real/eval --processed-dir artifacts/real/eval --split test --batch-size 1 --uncertainty-method none

# Export the selected checkpoint and verify ONNX on held-out tensors.
.\.venv\Scripts\python.exe scripts/export_verified.py --checkpoint artifacts/real/models/best.pt --index artifacts/real/processed/index.csv --onnx artifacts/real/model.onnx --output artifacts/real/runtime

# Infer the whole source series and restore the mask to its original grid.
.\.venv\Scripts\python.exe deploy/cli_infer.py --series-dir data/dicom_series_01 --checkpoint artifacts/real/models/best.pt --onnx-path artifacts/real/model.onnx --output-dir artifacts/real/prediction --output-formats mask
```

The last command produces a whole-series deployment artifact, while `infer.py --split test` produces held-out evaluation. They answer different questions. Dataset references resolve relative to the index directory, or to an explicitly supplied `CT25DDataset` data root. Move the complete processed directory together; do not change its frozen split after model selection.

Checkpoints store architecture, resize/preprocessing contracts, data hashes and selection provenance. Deployment rejects incompatible preprocessing or an ONNX graph from another checkpoint. Changing preprocessing requires preparing data and retraining under the new contract. Parameters and additional options are available through each script's `--help`.

## Deployment interfaces

### CPU CLI

The CLI explicitly selects ONNX Runtime's CPU provider and validates parity by default. ONNX uses opset 17, fixed checkpoint spatial dimensions and dynamic CPU batch. Provisional CPU gates require probability agreement at atol=1e-4/rtol=1e-3 and at least 99.9% mask agreement; failures exit nonzero.

Use `--mask-format nii.gz` for NIfTI instead of the default NPZ, and `--output-formats mask overlays` for local overlays. The mask is restored by inverse resize, crop and physical resampling, using nearest-neighbor labels. Cropped-out source regions are background. Origin, direction and spacing accompany the mask. `--disable-postprocess` allows raw deployment output; the recorded postprocessor worsens pseudo-label agreement, so interpret that choice explicitly and avoid tuning it on test data.

### Experimental localhost API

After creating matching artifacts, set their paths and start the service:

```powershell
$env:CT25D_CHECKPOINT = (Resolve-Path artifacts/real/models/best.pt).Path
$env:CT25D_ONNX = (Resolve-Path artifacts/real/model.onnx).Path
.\.venv\Scripts\python.exe -m uvicorn deploy.app:app --host 127.0.0.1 --port 8000
```

In a second terminal, check readiness and upload a ZIP containing exactly one supported series:

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe -f -X POST http://127.0.0.1:8000/predict -F "dicom_zip=@artifacts/series.zip" -o artifacts/prediction.zip
```

The caller must create `series.zip` from permitted data. `GET /health` returns 503 until model initialization succeeds. `POST /predict` returns a downloadable ZIP with `prediction_mask.npz` and `technical.json`. Uploads are limited to 64 MiB, expanded archives to 256 MiB and 512 files. Unsafe paths, symlinks, ambiguous series and unsupported geometry are rejected; temporary data is cleaned on success/failure. The runtime initializes once. This localhost service has no production or multi-user claim.

### CPU Docker image

After the synthetic quickstart creates input/model artifacts, build and run the CLI container in PowerShell:

```powershell
docker build -t ct25d-cpu .
$ctArtifacts = (Resolve-Path artifacts/synthetic).Path
docker run --rm --mount "type=bind,source=$ctArtifacts,target=/work" ct25d-cpu --series-dir /work/series --checkpoint /work/models/best.pt --onnx-path /work/model.onnx --output-dir /work/prediction --output-formats mask
```

The Dockerfile uses Python 3.12 and CPU PyTorch. Patient data/models are excluded from the build context and mounted at runtime. Linux CI has built and exercised the image with synthetic data. NPU deployment is separate; this CPU container does not provide Windows NPU passthrough.

## Intel NPU benchmarking

Create the **256 x 256 baseline** checkpoint, ONNX model and exported runtime tensors first. The measured hardware is Intel Core Ultra 7 155U with Intel AI Boost driver 32.0.100.5540 and OpenVINO 2026.3.1. A compatible environment can run the benchmark without PyTorch because export saves reference logits and targets.

```powershell
.\.venv\Scripts\python.exe scripts/benchmark_intel.py --onnx artifacts/real/model.onnx --inputs artifacts/real/runtime/runtime_inputs.npz --output artifacts/real/runtime/intel_benchmark.json --runs 30
```

The script compares ONNX Runtime CPU, OpenVINO CPU and explicitly selected OpenVINO NPU against the exported PyTorch reference. NPU compilation uses fixed `[1,3,256,256]` input. It records execution devices, precision, probability/label differences, model-grid Dice, compilation/first inference, warm p50/p95, throughput, threads/requests, power state and process memory. PyTorch CPU timing is recorded by export.

NPU success requires NPU-only execution evidence and a predeclared absolute Dice-drop threshold <=0.01. FP16 quality is separate from the tighter FP32 CPU probability gate; these are engineering investigation thresholds, not clinical acceptance criteria. Intel GPU experiments are optional and separate. See [reproduction details](docs/reproducibility.md) and the [recorded benchmark](reports/intel_benchmark.json).

## Recorded results

These measurements come from one local 34-slice, 512 x 512 CT series. Corrected preprocessing produces 30 x 239 x 208 voxels, with 18 train, four validation, four test and four excluded buffer centers. The source retains 5 mm z spacing. The results demonstrate software and runtime behavior; they do not establish unseen-patient performance.

| Measurement | Result | Evidence |
| --- | --- | --- |
| Raw foreground macro Dice / IoU | 0.30325 / 0.23449 | [Evaluation](reports/evaluation.json) |
| Postprocessed foreground macro Dice / IoU | 0.14451 / 0.09225 | [Evaluation](reports/evaluation.json) |
| Raw Dice, classes 1 / 2 / 3 | 0 / 0.77311 / 0.13663 | [Evaluation](reports/evaluation.json) |
| ONNX CPU maximum probability difference / mask agreement | 4.17e-7 / 100% | [CPU parity](reports/onnx_parity.json) |
| Warm p50: PyTorch / ONNX Runtime / OpenVINO CPU | 69.08 / 50.51 / 42.37 ms per stack | [Benchmark](reports/intel_benchmark.json) |
| Warm NPU p50 / p95 | 4.94 / 6.21 ms per stack | [Benchmark](reports/intel_benchmark.json) |
| FP16 NPU mask agreement / absolute Dice drop | 99.9943% / 0.000080 on model grid | [Benchmark](reports/intel_benchmark.json) |
| Required regression tests | 30 passed, zero skipped; lint passed | [Verification](reports/verification.json) |

Runtime measurements use identical tensors, three warmups and 30 repeats. They measure warm stack inference, not DICOM-to-mask latency. NPU metrics use the resized model grid; primary evaluation uses the processed grid. Application caching was disabled, driver caches were not reset, and reported peak memory is cumulative process working set. The results are specific to the recorded hardware/settings.

## Repository structure

```text
configs/                 Validated baseline training configuration
src/
  dicom_loader.py        DICOM/HU/geometry validation
  preprocessing.py       Resampling, ROI, normalization and inverse geometry
  public_metadata.py     Allowlisted technical metadata validation
  data/                  2.5D dataset, manifests, transforms and split checks
  baselines/             Classical candidate/pseudo-label generation
  models/                Compact U-Net, loss and metrics
  evaluation.py          Shared contiguous-volume postprocessing
  calibration.py         Guarded exploratory calibration
  robustness.py          Model behavior/uncertainty utilities
  visualization.py       Local overlays, plots and montages
scripts/                 Preparation, training, evaluation, export and benchmarks
deploy/                 CLI, reusable runtime and experimental API
tests/                  Synthetic correctness and deployment regressions
metadata/examples/      Reviewed technical example, without original identifiers
reports/                Selected sanitized metrics, provenance and environment evidence
docs/                   Detailed contracts, reproduction, validation and model card
artifacts/              Ignored generated models, tensors and local run outputs
Dockerfile              CPU CLI container
pyproject.toml          Package metadata and dependency extras
LICENSE                 MIT code license
```

`artifacts/` is created by commands. The historical `data/`, `data_processed/`, `saved_models/` and `outputs/` locations may contain ignored local files; a fresh checkout does not supply patient images or usable pretrained models there. The importable modules retain their existing package layout; a namespace migration is not required to run them.

## Testing and reproducibility

Run the required lint/regression checks with the selected environment:

```powershell
.\.venv\Scripts\python.exe scripts/check.py
```

The equivalent individual checks are `python -m ruff check src scripts deploy tests` and `python -m unittest discover -s tests -v`. Tests generate their own synthetic axial/oblique/rescaled/compressed DICOM and small model artifacts. Required checks fail when prerequisites are absent instead of reporting an all-skip success.

Coverage includes rescale-once/padding, malformed metadata, physical round trips, neighboring-slice support, epoch augmentation, empty-class metrics, graph/checkpoint contracts, CLI batch invariance, API readiness, safe archives and cleanup. [CI](.github/workflows/ci.yml) runs lint/tests on Windows and Linux; Linux also builds and runs the CPU Docker image. NPU verification is a separate local hardware job. [The main promotion run](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/37234017241) passed these hosted gates.

Reproduction evidence includes a fresh environment/separate checkout synthetic workflow, relocated real-data evaluation, matching evaluation masks across batch sizes 1/2/3 and source-grid CLI masks across batch sizes 1/3. The [validation table](docs/validation.md) links each requirement to tests or reports. Frozen data/index hashes, source-code provenance and model checksums prevent historical and corrected outputs from being silently mixed.

## Changes from previous versions

Version **0.8.0**, documented on **4 October 2026**, supersedes the historical sprint-era results and conflicting 0.7/1.0 status claims. Earlier source/results remain recoverable at commit `457ddbf`; an old local `best.pt` is not the repaired deployment model.

| Area | Earlier behavior or claim | Current behavior |
| --- | --- | --- |
| Data availability | README implied bundled DICOM; index referenced an old machine | No bundled patient/model artifacts; synthetic quickstart and relative, validated manifests. |
| HU and geometry | Compressed fallback risked repeated rescale; incomplete inverse mapping | Rescale-once/padding evidence, physical transforms and tested source-grid masks. |
| Splits | Adjacent stacks crossed split boundaries; patient-plus-series grouping | Complete support isolation, boundary buffers and patient grouping; same-series limits explicit. |
| Evaluation | Mixed splits, missing-held-out fallback and batch-local postprocessing | Explicit nonempty splits, physical ordering, contiguous-volume processing and global metrics. |
| Training/calibration | Repeated fixed-seed transforms and ambiguous calibration claims | Epoch-varying reproducible augmentation, traceable retraining and identity primary temperature. |
| Deployment | Limited parity checks and weak artifact contracts | Checked ONNX, declared gates, checkpoint/preprocessing binding and nonzero failure exits. |
| Intel acceleration | Device visibility/convolution smoke test only | Actual full U-Net NPU-only execution and comparable quality/latency evidence. |
| Service/package | Weak readiness/artifact handling; duplicate paths/dependencies | Bounded experimental API, reusable runtime, downloadable results, authoritative packaging and verified CPU container. |
| Documentation/repository | Competing day-by-day claims, tracked images/models, unused MONAI | Consolidated docs, sanitized reports, MIT code license and ignored local artifacts. |

The [dated change record](docs/release_notes.md) gives the complete update/commit history and outstanding requirements. The separate TODO file was retired after its relevant status was consolidated there and in validation documentation.

## Limitations and research requirements

The teacher is heuristic, class 1 is rare, overlap dominates central tissue and the current postprocessor reduces agreement. One same-series split, with whole-series preprocessing decisions, cannot establish clinical generalization. Uncertainty maps describe model behavior and are not validated clinical confidence. Thick slices, crop extremes, motion, metal, small structures and preprocessing changes may affect outputs.

Further research requires a clinically defined task, permitted expert-annotated multi-patient data, annotation review, patient/site/scanner separation, matched alternatives and external evaluation. Source-data rights must be established before publishing real images, original-file hashes or trained assets. The local sample's acquisition terms remain unknown, so its exact public reproduction is currently unavailable.

Public metadata follows a numeric technical allowlist; identifiers, original UIDs and machine paths are excluded. Aliases/checksums do not constitute full DICOM anonymization, and images need separate disclosure review. Git cleanup preserves history and does not erase previously committed identifiers. The project makes no CE claim; see [regulatory scope](docs/regulatory_scope.md) for the research/clinical distinction and official references.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Import error or missing tool | Install the required extras into the same virtual environment used to run the command. Run from the repository root. |
| Missing DICOM/checkpoint/model | Use the synthetic workflow, or acquire permitted CT and run preparation, training and export. A clean clone has no real pretrained assets. |
| Unsupported DICOM geometry or decoding | Check the input contract and one-series directory layout; install optional codecs for supported compressed input. Preserve validation failures for investigation. |
| Empty validation/test split | Use a sufficiently long case or define a valid research manifest; training data is never substituted for held-out data. |
| Manifest/checksum mismatch | Restore the frozen matching artifacts or regenerate preparation and retrain. Copy processed volumes and manifest files together. |
| Checkpoint, resize or preprocessing mismatch | Use the checkpoint's configuration and its verified ONNX graph; re-export the correct model or retrain after preprocessing changes. |
| API returns 503 | Check that both environment variables point to matching readable artifacts with valid contracts before starting the service. |
| NPU absent or compilation fails | Check supported hardware, driver and OpenVINO installation; use the required 256 x 256 graph and inspect recorded execution-device/error evidence. CPU remains the primary CLI path. |
| Low Dice or worse postprocessing | Inspect raw/classwise metrics and local failure overlays. Pseudo-label quality and same-series limits are part of the result; do not tune on the test split. |

## Documentation and license

- [Documentation index](docs/README.md)
- [Data acquisition, privacy and technical metadata](docs/data.md)
- [Architecture, labels, geometry and metric contracts](docs/architecture.md)
- [Detailed reproduction commands](docs/reproducibility.md)
- [Requirements and validation evidence](docs/validation.md)
- [Model card and intended-use limitations](docs/model_card.md)
- [Regulatory scope](docs/regulatory_scope.md)
- [Dated changes and remaining requirements](docs/release_notes.md)
- [Cleanup inventory](docs/cleanup.md)

Code is licensed under [MIT](LICENSE). That license grants no rights to source CT data or third-party assets. AI-agent implementation/testing assistance and the scope of human verification are recorded in the model card; no clinical expert approval is claimed.
