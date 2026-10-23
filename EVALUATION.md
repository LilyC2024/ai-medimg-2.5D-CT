# CT evaluation record

Software execution and clinical performance are separate. The recorded data are
generated CT-like phantoms; no new patient accuracy or reader-time benefit is
claimed. [Validation commands](docs/validation.md).

## Current documentation update

The companion is now named **LOVISA — Medical History & Clinical Reasoning
Assistant**. Guides distinguish its history/LLM/report role from CT's image/CV/
measurement role and retain the existing `mhcra-*` contracts. No detector, weights,
training or schema changes are part of this documentation pass. Local checks for this pass: **81 tests passed in 23.90s**, Ruff/active-package
format passed, and all 25 maintained Markdown files passed local-target checks.
LOVISA passed 146 tests in 42.35s plus actual local gemma4:e2b smoke; the
ML-free contract/renderer/report still match exactly. Hosted results follow
after publication.

## Verified v0.10 compatibility

| Executed check | Outcome |
| --- | --- |
| Nodule producer/review gate | 26 checks passed, including pending/reviewed export and adversarial mutations |
| Full CT suite | 81 passed in 25.74s |
| LOVISA companion suite | 146 passed in 44.55s |
| Actual fixture → LOVISA | 32×64×64; 1 non-ML candidate; 66 artifacts verified |
| Actual installed-pretrained CPU → LOVISA | 32×64×64; 1 candidate; 66 artifacts verified |
| Actual legacy → LOVISA | 20×48×48; 41 artifacts; ONNX parity passed |
| Approval status | No imaging/safety/final approval issued by actual smokes |
| Contract/renderer/report | Exact vendored match after one import rewrite |
| Lint, format, dependencies and local links | Passed |

[CT run 39922103738](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/39922103738)
passed at `e0704b22177a23b323e4d3aff455c447d0579542`: Windows/Linux, new fixture/
pretrained bridge commands, actual pretrained phantom inference and Linux Docker.
[LOVISA run 39922198090](https://github.com/LilyC2024/Medical-AI/actions/runs/39922198090)
passed at `607c8a586fc820f9757b5b5a9b715247005df52f`: Python 3.10/3.12, contract
equality and actual fixture/pretrained/legacy receiver checks.

## Earlier lung-model evidence

| Check | Recorded result |
| --- | --- |
| v0.9 portable regression | 68 tests, 19.69s after Windows UTF-8 fixes |
| Official weights | ~80 MB checkpoint loaded strictly with tensor-only loading |
| Actual CPU phantom detection | One candidate; 6.08s including model load in recorded smoke |
| Warmed phantom latency | p50 3.29s / p95 3.32s over three recorded warm runs |
| Upstream trainer construction | Real MONAI DetectionTrainer created on CPU/generated data; no training loop |
| Review blocking | Actual pretrained smoke could not produce an approved report |
| Device inspection | CPU-only torch; CUDA unavailable; OpenVINO not installed |
| Local Docker | Daemon access blocked; hosted container checks passed separately |

[Pretrained smoke JSON](reports/lung_pretrained_smoke.json) records source/model/
recipe hashes and versions; [latency JSON](reports/lung_cpu_latency.json) records
the experiment. Small-phantom timing is not full clinical CT latency. Scripted
review attestations in tests are not clinician approval.

## Coverage and limits

Tests cover source-byte integrity, geometry/RAS-LPS mapping, real random-weight
network/tiled forward, explicit unavailable-device failures, review completeness,
caliper bounds, report regeneration, allocation limits, dataset hash/patient splits,
negative scans and duplicate FROC detections. GPU execution is not inferred from
these tests.

No independent patient cohort, external sensitivity, cancer classification,
new-model NPU result, actual CUDA training or reader study exists. Upstream metrics
cannot be inherited by the adapted inference recipe. Public research permission
and expert annotations remain the operator's responsibility.

Legacy tissue-pipeline Dice, ONNX parity and measured Intel NPU timings are separate
historical evidence. [Legacy guide](docs/legacy-pipeline.md) ·
[Report inventory](reports/README.md) · [Intended use](docs/regulatory_scope.md).
