# Current compatibility evaluation — 23 October 2026

| Executed check | Outcome |
| --- | --- |
| Nodule-v2 producer/review phase gate | 26 tests passed; pending/reviewed exports and adversarial mutations |
| Full CT regression | 81 passed in 25.74s (final local rerun); legacy and current nodule tests included |
| Lint/format | Ruff src/scripts/deploy/tests and full active-package F checks/format passed |
| Actual MHCRA fixture worker/receiver | Passed: 32×64×64 source, 1 fixture candidate, 66 validated artifacts |
| Actual MHCRA pretrained worker/receiver | Passed: installed official weights, CPU, 1 candidate, 66 artifacts |
| Actual legacy worker/receiver | Passed: 20×48×48 source, 41 artifacts, producer ONNX parity passed |
| Approval state in all actual smokes | No imaging acceptance or final report approval issued |
| Companion final offline regression | 146 tests passed in 44.55s; includes nodule caliper UI and urgent-routing checks |
| Shared contract | Byte-identical schemas/report/renderer after MHCRA import-path rewrite |

These smokes process generated pixels only, not real patients. Pretrained and
non-ML fixture execution are reported separately. No new detector training,
clinical accuracy, reading-time benefit, actual CUDA or new NPU execution is
claimed. MHCRA performs its own authenticated imaging and final report reviews;
unit/UI review identities are scripted tests, not clinicians. Current hosted
release checks passed as recorded below.

## Current hosted verification

[CT Actions run 39922103738](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/39922103738)
passed for implementation `e0704b22177a23b323e4d3aff455c447d0579542`: Windows and
Linux regression/lint, fixture bridge, real pretrained smoke/bridge and Linux
Docker checks. [MHCRA run 39922198090](https://github.com/LilyC2024/Medical-AI/actions/runs/39922198090)
passed for consumer `607c8a586fc820f9757b5b5a9b715247005df52f`, with Python
3.10/3.12 tests, exact contract equality and real fixture/pretrained/legacy
producer-consumer smoke. Local CUDA/NPU remains unexecuted; no clinical
performance is inferred. This documentation-only record does not change the
tested code or the consumer's pinned producer contract.

## Previous lung research evaluation — 22 October 2026


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
| Windows portability repair regression | 68 tests passed, 19.69s; explicit UTF-8 IO, Unicode review round trip and simulated cp1252 documentation regression |
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
| Hosted release CI | Windows and Linux regression jobs, real pretrained phantom smoke and Linux Docker checks all passed at implementation commit 5bb2c9b |

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

The first hosted Windows run caught a UTF-8 documentation read using the platform
default cp1252 codec. All new text-file IO now specifies UTF-8; regressions cover
a simulated Windows default and Unicode reviewer/report round trips. New package
formatting and full F-category lint checks were added. Hosted matrix fail-fast is
disabled so Windows errors do not cancel independent Linux/container evidence.
The initial run's pretrained smoke passed; its Windows failure and cancelled Linux
container step are not presented as successful release validation.

## Published validation

[Repaired release CI](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/39850836849)
passed all three jobs for implementation commit
`5bb2c9b79191001387468d8094280442352b21ab`: Windows and Linux full suites,
source/documentation/style/dependency checks, fixture and legacy MHCRA producer
commands, actual pretrained phantom inference, and Linux CPU Docker build/run
for both the new nodule demo and retained legacy ONNX path. No GPU/NPU or patient
data execution occurred in those jobs. The earlier failed run is superseded.
The following documentation-only publication record does not change tested code.

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
