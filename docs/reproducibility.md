# Reproduce the retained legacy experiment

[Current lung setup](../README.md) · [Legacy synthetic quickstart](legacy-pipeline.md)

Use Python 3.12 with the `ml` extras. `pyproject.toml` is authoritative;
requirements.txt forwards to it. Windows constraints describe recorded versions,
not a universal cross-platform lock. Run `python -m pytest -q`, not unittest alone,
to collect both current and legacy tests.

## Permitted-data baseline

Use the generated fixture or an independently permitted supported series. The
historical real sample has no verified public download. From the repository root:

```bash
.venv/bin/python scripts/prepare_case.py --series-dir data/permitted-series --output-dir artifacts/legacy/processed
.venv/bin/python scripts/train.py --config configs/baseline.json --index-path artifacts/legacy/processed/index.csv --output-dir artifacts/legacy/train --model-dir artifacts/legacy/models
.venv/bin/python scripts/infer.py --index-path artifacts/legacy/processed/index.csv --checkpoint artifacts/legacy/models/best.pt --output-dir artifacts/legacy/eval --processed-dir artifacts/legacy/eval --split test --batch-size 1 --uncertainty-method none
.venv/bin/python scripts/export_verified.py --checkpoint artifacts/legacy/models/best.pt --index artifacts/legacy/processed/index.csv --onnx artifacts/legacy/model.onnx --output artifacts/legacy/runtime
.venv/bin/python -m deploy.cli_infer --series-dir data/permitted-series --checkpoint artifacts/legacy/models/best.pt --onnx-path artifacts/legacy/model.onnx --output-dir artifacts/legacy/prediction --output-formats mask
```

Frozen splits/hashes precede model selection. Move the processed directory intact;
use explicit data_root when needed. `infer --split test` evaluates held-out centers;
whole-series CLI output is a different artifact. Loading is tensor-only with exact
architecture/preprocessing checks; there is no arbitrary pickle fallback.

## Intel NPU comparison

Use the recorded 256×256 graph and exported identical input/reference tensors.
Install compatible OpenVINO/Intel driver separately (`.[intel]`):

```bash
.venv/bin/python scripts/benchmark_intel.py --onnx artifacts/legacy/model.onnx --inputs artifacts/legacy/runtime/runtime_inputs.npz --output artifacts/legacy/intel-benchmark.json --runs 30
```

Historical hardware was Core Ultra 7 155U, driver 32.0.100.5540, OpenVINO 2026.3.1.
The benchmark records explicit execution devices, compile/first/warm timings,
precision and numeric/label/Dice agreement. NPU success requires NPU-only evidence.
CPU/NPU gates differ. Cumulative process memory is not device RAM; caches/power/
thread settings matter. This is not new-detector acceleration evidence.

## Experimental legacy API and container

Set CT25D_CHECKPOINT and CT25D_ONNX to matching local artifacts, then launch
`python -m uvicorn deploy.app:app --host 127.0.0.1 --port 8000`.
`GET /health` stays 503 until initialization; `POST /predict` accepts one supported
ZIP and returns source mask plus numeric technical metadata. Limits: 64 MiB
compressed, 256 MiB expanded and 512 files. Invalid paths/geometry fail and temporary
files are removed. This is a localhost experiment, not a clinical/multi-user API.

The current Docker image defaults to the **lung CLI**. To run legacy inference,
override the entrypoint explicitly:

```bash
docker build -t lung-research .
docker run --rm --entrypoint python -v "$PWD/artifacts/legacy:/work" lung-research -m deploy.cli_infer --series-dir /work/series --checkpoint /work/models/best.pt --onnx-path /work/model.onnx --output-dir /work/prediction --output-formats mask
```

Use generated source in `/work/series` for this example. Models/data are mounted,
not bundled. Hosted Linux CI exercised both paths. Local Docker verification was
blocked by daemon access; no local container pass is claimed. [Evidence](validation.md).

## Documentation and source identity

Run `scripts/generate_api_docs.py --check` and `scripts/check_docs.py` alongside
software checks. The latter verifies local heading anchors as well as file paths;
external links are not fetched. Current expert repairs and tests are separate
from historical measurements in this guide. Reproduce an old run with its own
recorded model/config/input, not by substituting a current nodule detector.
[Findings](review.md) · [Current validation](validation.md).
