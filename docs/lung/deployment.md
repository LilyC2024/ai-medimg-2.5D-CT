# Run the CT project on local hardware

[Overview](../../README.md) · [Training](training.md) · [Actual results](../../EVALUATION.md)

CT runs in its own Python 3.12 environment. LOVISA uses its separate environment
and starts CT through a bounded local worker; see [Integration](mhcra.md).

## Choose the execution device

| Hardware | Active nodule workflow | Evidence/status |
| --- | --- | --- |
| CPU | Pretrained inference, UI, fixtures and tests | Executed locally on generated CT |
| NVIDIA CUDA | Explicit inference and upstream training launcher | Implemented; no CUDA device available for execution here |
| Intel Core Ultra 7 155U / NPU | Historical fixed-shape 2.5D ONNX/OpenVINO experiment | Measured in earlier project; not a 3D nodule result |
| Intel NPU for new 3D RetinaNet | No supported production backend in this release | No export, parity, memory or device execution evidence |

The recorded Windows PC has Intel Core Ultra 7 155U and NPU driver 32.0.100.5540.
The current development environment is Linux with CPU-only torch and no OpenVINO.
Do not infer current hardware from old report metadata. `scripts/lung_hardware.py`
records devices actually visible. There is no AUTO/HETERO accelerator routing.

## Install a matching runtime

Reuse Python 3.12 .venv. Install matching torch/torchvision builds from the same
backend index. The executed CPU pair is torch 2.14.1+cpu / torchvision 0.29.1+cpu,
with MONAI 1.6.1 and nibabel 5.4.2. A generic torchvision wheel against CPU torch
caused a missing torchvision::nms operator; matching CPU wheels fixed it.
For CUDA select the appropriate official build for your driver, then install
project extras. Do not copy the CPU command onto a CUDA training environment.

`fetch-model` is an explicit network setup action using a pinned official revision.
It downloads roughly 80MB of weights plus configs/scripts/licenses. Inference
validates local files and never automatically downloads. Missing/incompatible
files fail; download a fresh registration directory rather than editing hashes.
Upstream training scripts are third-party executable code; review them and their
license before launching training. Inference constructs the network locally and
does not evaluate upstream JSON expressions.

## Verify execution and measure latency

```bash
.venv/bin/python scripts/smoke_lung.py --model-dir models/luna16 --device cpu --output artifacts/smoke.json
.venv/bin/python scripts/benchmark_lung.py --series artifacts/lung-demo/series --model-dir models/luna16 --device cpu --runs 5 --output artifacts/latency.json
```

Add research approval for public data; use cuda only on a working CUDA environment.
Latency separates model load, first run and warmed p50/p95 and includes DICOM IO,
hashing, preprocessing, detection and source mapping. It excludes clinician review.
Phantom latency does not predict full-size chest CT latency. Keep protocol, volume
size, model hash, hardware, driver, precision and power state with comparisons.

## Retained Intel engineering experiment

The [legacy benchmark](../../scripts/benchmark_intel.py) compares identical fixed
2.5D tensors across PyTorch/ONNX Runtime/OpenVINO and verifies NPU-only execution
and numeric/label agreement. [Recorded evidence](../../reports/intel_benchmark.json)
is historical. This remains useful deployment practice for CV/engineering work.
Adapting 3D RetinaNet to Intel hardware requires a separate supported export,
operator/shape audit, source-level candidate parity and measured device execution.
Do not apply old 4.94ms per-stack timing to the new full-volume detector.

## Local container and review interface

The CPU Docker image's default command is the new nodule CLI. Weights/data must
be mounted locally; none are baked into the image.

```bash
docker build -t lung-research .
docker run --rm -v "$PWD/artifacts:/work" lung-research demo --output /work/docker-demo
```

Use a new output directory on each run. The old deployment CLI remains available
via an explicit entrypoint override; see [legacy guide](../legacy-pipeline.md).
The Streamlit UI is launched from the installed local environment as documented
in the main README, bound to 127.0.0.1. It has no multi-user authentication or public
hosting support. Workspaces contain image pixels and belong outside Git.

## Troubleshooting

| Error | Action |
| --- | --- |
| torchvision::nms missing | Reinstall matching torch/torchvision backend wheels |
| Registration mismatch | Re-fetch fixed model into a new directory; never bypass hash checks |
| CUDA unavailable | Inspect driver/device; explicitly use CPU for inference, not a fake GPU run |
| NPU requested | New detector does not support it; retain historical experiment separately |
| Workspace already exists | Choose a new output; snapshots are not overwritten |
| Review remains blocked | Resolve every candidate and check explicit attestations/caliper bounds |
| Training memory error | Consult upstream batch/patch settings; record changes and re-evaluate |
| Unsupported CT geometry | Use a supported research series; do not discard slices silently |

## Input failures versus device failures

Use a fresh workspace for a successful new study. Invalid source shape/nonfinite/
nonrepresentable pixels now fail before creating it, so corrected input can retry
the same unused destination. Do not fix a registration mismatch by editing hashes;
reinstall or re-register the actual intended assets.

LOVISA's prepared ZIP route validates existing results, not full-volume detection.
Its installed-model example uses generated bounded pixels. Full-scan CPU work can
outlast interactive budgets and belongs offline. The retained API owns upload
extraction lifetime and reports encrypted/duplicate members as invalid input.
[Review](../review.md) · [Current setup](../setup.md).
