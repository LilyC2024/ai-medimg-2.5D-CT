# Install and launch the CT companion

[Overview](../README.md) · [Hardware detail](lung/deployment.md) · [Validation](validation.md)

## Existing checkout

Use Python 3.12; inspect `.venv/bin/python --version`, installed packages and
`pip check` before changing dependencies. Keep CT separate from LOVISA and
endoscopy. The root README has fresh Linux CPU commands. The full development
extras include legacy ONNX/API dependencies so the retained suite can run.

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install torch==2.14.1+cpu torchvision==0.29.1+cpu --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python.exe -m pip install -e ".[ml,lung,ui,dev]"
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m lung_nodule.cli demo --output artifacts/first-example
.venv\Scripts\python.exe -m streamlit run src/lung_nodule/ui.py --server.address=127.0.0.1 --server.port=8502
```

Open the generated `workspace` directory in the source-first UI. Output names are
immutable; use a new directory for a new study. No reviewer decision is supplied
by the demo command.

## Install the pretrained model explicitly

```bash
.venv/bin/python -m lung_nodule.cli fetch-model --output models/luna16
.venv/bin/python scripts/smoke_lung.py --model-dir models/luna16 --device cpu --output artifacts/pretrained-smoke.json
```

The setup command downloads a pinned official revision and retains its licenses.
Runtime detection checks registered file/config identities, loads tensor-only
weights and never fetches missing assets. If an installed directory is already
registered, reuse it instead of overwriting or changing its manifest.

For supported research DICOM, supply explicit permission/protocol approval and
use `lung_nodule.cli detect`; a screenshot or one PNG is insufficient. [Source
requirements](lung/data.md) · [Real excerpt reproduction](lung/public-demo.md).

## Devices and offline work

| Work | Supported path |
| --- | --- |
| Synthetic fixture | CPU, no weights |
| Pretrained lung inference | Explicit CPU or available CUDA |
| Full upstream lung training | CUDA and required memory; no automatic CPU/NPU fallback |
| New detector on Intel NPU | Not implemented/validated |
| Historical 2.5D model | Separate ONNX/OpenVINO deployment exercise |

Install torch/torchvision builds matching the intended backend. A missing CUDA
runtime or `torchvision::nms` mismatch is an installation error, not permission to
silently change devices. [Detailed troubleshooting](lung/deployment.md).

Bind UI/API to loopback. There is no standalone multi-user authentication or
clinical-patient portal. Large-volume preparation/training is offline; LOVISA's
interactive worker uses bounded artificial inputs or prepared excerpt evidence.
