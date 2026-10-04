# CT 2.5D research prototype — 0.8.0

This project measures a compact U-Net's agreement with classical CT head-region pseudo labels. It is for software engineers and imaging researchers inspecting ingestion, geometry, training and runtime behavior. It does not diagnose lesions or demonstrate clinical accuracy.

Raw DICOM, derived patient images and trained models are **not bundled in a clean checkout**. The local sample's acquisition source and redistribution permissions remain unverified. A synthetic fixture supports all required automated tests without external data. Historical results from commit `457ddbf` are superseded; do not compare them as if they used the corrected pipeline.

## Verified Windows quickstart

Run from the repository root with Python 3.12. The commands use the virtual environment executable explicitly. Install CPU PyTorch first; `pyproject.toml` is the dependency authority and the constraints record the tested Windows versions.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[ml,dev]" -c reports/windows-constraints.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m ruff check src scripts deploy tests
.\.venv\Scripts\python.exe scripts/generate_fixture.py artifacts/synthetic/series
.\.venv\Scripts\python.exe scripts/prepare_case.py --series-dir artifacts/synthetic/series --output-dir artifacts/synthetic/processed
.\.venv\Scripts\python.exe scripts/train.py --index-path artifacts/synthetic/processed/index.csv --output-dir artifacts/synthetic/train --model-dir artifacts/synthetic/models --epochs 1 --image-size 32,32 --base-channels 2
.\.venv\Scripts\python.exe scripts/export_verified.py --checkpoint artifacts/synthetic/models/best.pt --index artifacts/synthetic/processed/index.csv --onnx artifacts/synthetic/model.onnx --output artifacts/synthetic/runtime
.\.venv\Scripts\python.exe deploy/cli_infer.py --series-dir artifacts/synthetic/series --checkpoint artifacts/synthetic/models/best.pt --onnx-path artifacts/synthetic/model.onnx --output-dir artifacts/synthetic/prediction --output-formats mask
```

Success means tests execute, lint exits zero, case preparation prints validated split counts, training saves `best.pt`, export prints `within_tolerance: true`, and CLI writes `prediction_mask.npz` on the **source CT grid** with origin, direction and spacing. Synthetic performance has no anatomical interpretation. Missing real data fails with a link to acquisition instructions.

## Actual evidence

See [validation](docs/validation.md) for requirements and evidence, [evaluation](reports/evaluation.json), [CPU parity](reports/onnx_parity.json), and [full-model Intel benchmark](reports/intel_benchmark.json). These are small sanitized reports; local images and runtime tensors remain ignored. The single-series demonstration uses disjoint neighboring-slice support; it cannot establish generalization to new patients.

The corrected run has 18 train, 4 validation, 4 test and 4 buffer centers. Raw test foreground macro Dice is approximately 0.303; existing postprocessing reduces it to approximately 0.145. Scores measure agreement with the same teacher used for supervision. The class called bone is a broad threshold candidate, not an expert anatomical label.

The complete U-Net executes on the Intel NPU with explicit device evidence. FP16 NPU results are reported separately from FP32 CPU parity. Latency is warm stack inference, not full DICOM-to-mask latency; see the benchmark JSON for sample counts, precision, threads, compilation and first inference.

## Documentation

- [Data, privacy and acquisition](docs/data.md)
- [Architecture, pseudo-label and geometry contract](docs/architecture.md)
- [Commands and reproduction](docs/reproducibility.md)
- [Requirements and validation](docs/validation.md)
- [Model card](docs/model_card.md)
- [Regulatory scope](docs/regulatory_scope.md)
- [Repair notes and remaining work](docs/release_notes.md)
- [Detailed task status](CT_Project_TODO.md)

CLI is the validated deployment path. The localhost API is experimental and returns a ZIP containing a mask and technical metadata. The CPU Docker image was built and exercised by [Linux CI](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/37233373549). Code is MIT licensed; that license grants no rights to source data or third-party assets. Historical source and results remain recoverable in Git history.
