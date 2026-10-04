# Reproduction commands

Install with the README's Python 3.12 CPU commands first. Dependencies are defined by pyproject; `requirements.txt` forwards to it. Windows constraints record the measured versions, not a universal cross-platform lock. The environment evidence, source hashes and frozen index hashes link every run to its implementation. Historical checkpoint loading uses weights_only=True and exact architecture loading; no arbitrary-pickle compatibility fallback exists.

## Synthetic verification

The README commands generate a tiny CT, prepare its labels/index, train a small smoke model, validate ONNX, and execute CLI. Tests generate their own axial/oblique/rescaled/RLE DICOM, checkpoint and ONNX files in temporary directories. Required tests execute without real files or pretrained assets. `python -m unittest discover -s tests -v` and lint must exit zero. CI runs these on Linux and Windows CPU; NPU is a local hardware job.

## Real-data baseline

Prerequisite: acquire a permitted supported CT using data.md; the local historical sample has no verified public download. These commands write ignored local artifacts:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_case.py --series-dir data/dicom_series_01 --output-dir artifacts/real/processed
.\.venv\Scripts\python.exe scripts/train.py --index-path artifacts/real/processed/index.csv --output-dir artifacts/real/train --model-dir artifacts/real/models
.\.venv\Scripts\python.exe scripts/infer.py --index-path artifacts/real/processed/index.csv --checkpoint artifacts/real/models/best.pt --output-dir artifacts/real/eval --processed-dir artifacts/real/eval --split test --batch-size 1 --uncertainty-method none
.\.venv\Scripts\python.exe scripts/export_verified.py --checkpoint artifacts/real/models/best.pt --index artifacts/real/processed/index.csv --onnx artifacts/real/model.onnx --output artifacts/real/runtime
.\.venv\Scripts\python.exe deploy/cli_infer.py --series-dir data/dicom_series_01 --checkpoint artifacts/real/models/best.pt --onnx-path artifacts/real/model.onnx --output-dir artifacts/real/prediction --output-formats mask
```

Preparation validates every reference, shape and class ID and saves transform/config/checksum metadata. Training rejects missing validation, writes loss/metric histories, checkpoint provenance and checksum, and selects using validation only. Inference writes raw and postprocessed global metrics, failure slices, local overlays and NPZ predictions. Export checks the graph and all held-out tensors; failed parity exits nonzero. CLI emits a source-grid mask with numeric geometry, a preprocessing report and runtime report. This CLI does not silently attach full-series metrics to a held-out report. Local overlays are not public assets.

`CT25DDataset(index, data_root=...)` resolves references against an explicit root; otherwise references are relative to the index parent. Copy the complete processed directory to another location and run the same index command to test portability. Manifests are frozen and checksummed before training. Do not edit the split after selecting a checkpoint.

## Intel NPU

Windows prerequisite: supported Intel NPU driver plus `pip install -e ".[intel]"` in an environment compatible with OpenVINO. The measured machine is Core Ultra 7 155U with OpenVINO 2026.3.1 and driver evidence supplied in the initial setup. The benchmark can also run from an inference-only environment with numpy, onnxruntime and openvino, using tensors exported by the training environment.

```powershell
.\.venv\Scripts\python.exe scripts/benchmark_intel.py --onnx artifacts/real/model.onnx --inputs artifacts/real/runtime/runtime_inputs.npz --output reports/intel_benchmark.json --runs 30
```

Output identifies EXECUTION_DEVICES, precision hint, first inference, compile time, warmup, p50/p95, throughput, process memory, probability/label differences and held-out Dice on the model grid. CPU has one thread and one request; NPU uses one request. Application model caching is disabled; driver/internal caches were not reset, so repeated compilation may be warm. CPU probability gates and NPU quality gates are separate; compiler failures are recorded. NPU-only device evidence is required for an NPU success claim. Timings are sequential warm measurements, not power/energy measurements or universal speedup claims.

## Experimental service and container

Set CT25D_CHECKPOINT and CT25D_ONNX to the matching files, then:

```powershell
.\.venv\Scripts\python.exe -m uvicorn deploy.app:app --host 127.0.0.1 --port 8000
```

GET /health returns 503 until runtime initialization succeeds. POST /predict accepts one ZIP and returns downloadable prediction.zip containing source-grid mask and sanitized technical geometry. Upload limit 64 MiB; uncompressed archive limit 256 MiB; 512 files; image limits in data.md. Traversal, symlinks and ambiguous directories are rejected. Temporary extraction and output directories are removed on success/failure. Service tests cover valid, malformed, oversized and unavailable-model behavior. No production or multi-user service claim is made.

Dockerfile is a CPU CLI recipe using Python 3.12 and CPU PyTorch, with patient/model artifacts excluded from build context. The Linux CI job builds and exercises the CPU image with generated synthetic inputs; a successful hosted result is required to close this gate. No Docker engine is installed on the local host. Mount permitted data and matching models at runtime; the CPU container does not promise Windows NPU passthrough.
