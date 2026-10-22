# Evaluation — lung research release, 22 October 2026

Software behavior and clinical performance are different. No new patient dataset,
clinical sensitivity, cancer diagnosis accuracy or reading-time study is claimed.

## Executed locally

| Check | Actual outcome |
| --- | --- |
| Baseline before changes | 32 legacy tests passed, 13.81s |
| Foundation gate | 6 new geometry/source/approval/invalid-input tests passed |
| Detection gate | 10 cumulative new tests passed; real pretrained inference executed separately |
| Initial review gate | 20 cumulative new tests passed, including Streamlit AppTest and approval blocking |
| Research gate | 29 cumulative new tests passed; later UI/launcher regressions added |
| Intermediate full suite | 63 tests passed, 18.43s, including 32 legacy compatibility tests |
| Final expanded regression | 66 tests passed, 19.50s on the final local rerun; includes actual random-weight network/sliding-window forward and allocation/anisotropic-resolution regressions |
| Lint | Ruff passed on src/scripts/deploy/tests |
| Dependency consistency | pip check passed |
| Real pretrained weights | Official ~80MB checkpoint loaded strictly with tensor-only torch.load |
| Actual generated-phantom inference | Current bounded-window recipe passed; one candidate, 6.08s including load on CPU; not clinical accuracy |
| CPU latency command | 3 warmed generated-phantom runs recorded separately; p50 3.29s/p95 3.32s in this shared host run; not full clinical CT latency |
| Upstream training configuration | Real MONAI DetectionTrainer constructed on CPU/generated data; no training loop or CUDA execution |
| Unapproved report | Blocked in actual pretrained smoke; no review approval issued |
| Generated figure | Source pixels, fixture candidate and 8mm caliper rendered; no patient pixels |
| Device inventory | CPU-only torch; CUDA unavailable; OpenVINO not installed |
| Companion compatibility | Unchanged MHCRA suite: 120 passed in 32.72s |
| Local Docker attempt | Blocked: account lacks access to Docker daemon socket; no local container pass claimed |

[Pretrained smoke JSON](reports/lung_pretrained_smoke.json) records versions,
checkpoint/recipe hashes, candidate count and report gate. Timing is a small
32x64x64 phantom result, not full-size chest CT or end-to-end clinician latency.
Automated reviewer identities are scripted tests, not clinician review.

## Coverage

- Physical coordinate round trips, RAS/LPS mapping and source-grid boxes.
- Source-byte tampering, unique ordered SOP identities and separate research approval.
- Fixture positive/negative volumes and rejection of research input by fixture path.
- Missing/unavailable accelerators fail rather than silently falling back.
- Every candidate reviewed exactly once; uncertainty, false/string approval,
  stale study digests and invalid/rejected calipers block completion.
- Source/report changes cannot bypass recomposition or approval.
- Streamlit unattested rejection and explicit scripted synthetic approval paths.
- Patient/hash split leakage, duplicate studies, incomplete annotations, invalid
  paths, NIfTI identity and preprocessing spacing checks.
- FROC duplicate detection/negative scan behavior and train/validation-only launcher
  configuration. Launcher tests use a scripted subprocess; they are not GPU training.
- Legacy DICOM, U-Net, ONNX/parity, API and MHCRA v1 tests remain in the full suite.

## Observed issue and fix

A generic torchvision wheel against CPU-only torch failed with a missing
torchvision::nms operator. Installing matching CPU torch/torchvision wheels fixed
network construction and real pretrained inference. Setup, Docker and CI now
install that backend pair together. Upstream Orientation defaults emit a future
warning; other warnings come from the retained FastAPI/legacy ONNX export path.
They are recorded rather than suppressed or mislabeled as clinical failures.

## Unexecuted / limitations

- No CUDA GPU training or CUDA inference was executed on this host.
- No export, parity or actual Intel NPU execution exists for the new 3D detector.
  Old Intel results apply only to the historical 2.5D tissue model.
- No independent clinical detection evaluation, segmentation model, malignancy
  classification, lesion tracking, clinician reader study or real clinical approval.
- Protocol/coverage/completeness are operator attestations, not machine verification.
- New nodule exchange is not supported by the current MHCRA importer; old v1
  compatibility remains separate and tested.
- Hashes and local reviewer names are consistency/attestation mechanisms, not
  independent provenance authentication or verified professional credentials.
- Hosted CI results are recorded after execution; workflow presence alone does not
  establish success. Local Docker was attempted and blocked by daemon permissions.

See [training evaluation](docs/lung/training.md), [model card](docs/lung/model-card.md)
and [historical validation](docs/validation.md) for separate scopes.
