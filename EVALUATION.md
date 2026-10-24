# CT evaluation record

## Expert source review — 24 October 2026

Independent CT review repaired upload cleanup ownership, duplicate/encrypted ZIP
handling, class labels before integer conversion, finite real training HU, and
workspace preflight before reserving an output directory. Eighteen regressions
cover the demonstrated defects. [Detailed review](docs/review.md).

| Executed check | Actual outcome |
| --- | --- |
| Final full regression | **105 passed in 29.40s**, including 18 source-review and four documentation regressions |
| Source-repair suite before documentation phase | 101 passed in 34.96s; subsequent targeted review/docs 22 passed in 6.19s |
| Actual installed MONAI CPU phantom smoke | **8.39s**, one candidate, unreviewed reporting blocked; no review issued |
| LOVISA actual interoperability | Fixture/pretrained nodule-v2: 66 artifacts each; retained tissue-mask-v1: 41 artifacts; all pending review |
| Documentation/source checks | 31 maintained Markdown files/anchors, generated API freshness, source compilation, pip consistency, full applicable Ruff and lung formatting passed |
| Shared contracts | Exact LOVISA-vendored contract/renderer match; no wire/schema change |

The 11 warnings are existing legacy Starlette/httpx, ONNX/TorchScript/tracing and
MONAI/NumPy deprecations. API regression inference is scripted; the separate
pretrained smoke above actually executed installed weights on generated pixels.
No model/dataset/dependency/actual approval was changed. No full CT training,
CUDA, new-detector NPU or new clinical accuracy result is claimed. Previous ROI
inference remains a separately labelled annotation-selected localization smoke.

Root documentation is concise; detailed setup, geometry, training, review,
security, integration and source references are linked. Local-only source sketches
contain no medical images. Historical experiments below retain their original
models/data/measurement limitations; their metrics are not detector validation.
Publication and hosted outcomes are recorded after execution below.

## Real CT excerpt and LOVISA research evidence — 23 October 2026

- Final local regression: **83 passed in 34.61s**, with 11 existing dependency/legacy-export warnings. New tests cover exact public crop geometry, pending exports and scripted excerpt-to-source candidate mapping.
- Actual source: official public TCIA **LIDC-IDRI-0002**, 261 DICOM slices, source 512×512 per slice, CC BY 3.0. Contrast status is not supplied; the explicit public-research protocol remains unverified. Deidentified dates were not used as true acquisition dates. LIDC-IDRI-0001 was inspected during selection and excluded because contrast was documented.
- The attempted whole-scan CPU run was **stopped after roughly 28 minutes without a completed result**. It is not reported as a successful full-scan test. Full RetinaNet training was **not executed**: CUDA is unavailable and the existing full trainer requires a >=16-GB CUDA GPU and a proper larger cohort.
- The final **32×96×96 source ROI**, origin `(168,313,300)`, was selected from the first source-matched official reader contour before inference. Actual registered MONAI CPU inference took **11.98s**, proposing one candidate. An earlier 16-slice probe took 21.29s under concurrent load and clipped the annotated lesion extent; the wider final ROI replaced it.
- XML localization smoke: two included reader contour observations, both matched by the declared predicted-center/contour-box proxy with 2-mm margin; zero out-of-scope observations. This is annotation-selected localization, **not detection accuracy**, consensus, pathology, FROC or independent evaluation. LUNA pretraining overlap is possible. [Exact evidence](reports/lidc0002-excerpt32-localization.json).
- Actual research-v3 producer -> LOVISA validator passed with source HU, all excerpt previews, original source metadata/hashes, exact crop translation and explicit actual-inference coverage. No resampling, inferred acquisition date or automatic caliper was introduced.
- Combined real CT/endoscopy + actual local Ollama smoke passed in **34.32s**, four embedded source/annotation images and 170 report words. All approvals were **scripted in an isolated temporary database**, not clinical reviews or updates to the actual app.

The prepared local demo links this CT to a fictional composite case with unrelated
Kvasir endoscopy imagery; no real-patient or common-disease linkage is asserted.
Research datasets, DICOM/JPEG pixels and model weights stay outside Git. Runtime
remains local. [Reproduce this demo](docs/lung/public-demo.md).

The sections below are historical release records with their then-current scope.

Software execution and clinical performance are separate. Earlier records use generated CT-like phantoms. The public-data extension below
adds an annotation-selected real CT ROI smoke; no independent patient accuracy
or reader-time benefit is claimed. [Validation commands](docs/validation.md).

## LOVISA concise-report documentation alignment — 23 October 2026

Updated README and integration/model-card guides to describe LOVISA's one-section
summary, accepted CT inspection/pictures, previewed clinician note and offline HTML
export. Existing `mhcra-*` contracts, detector, measurements, training and
standalone research report are unchanged.

Local checks: **81 tests passed in 22.42s**, with 11 existing dependency/legacy
export warnings; all **25** maintained Markdown files passed local-target checks.
LOVISA's new report implementation passed **220 tests in 79.04s** and the exact
shared-contract check. Its actual pretrained CPU transfer verified one generated
candidate and 66 artifacts without issuing approvals. Report/example tests use
scripted model/reviewer identities; they are not clinical validation.

This is a documentation-only publication. Existing producer-code hosted results
remain applicable; LOVISA's release checks exercise the pinned producer again.
[Current report guide](https://github.com/LilyC2024/Medical-AI/blob/main/docs/REPORTS.md).

## Current documentation update

The companion is now named **LOVISA — Medical History & Clinical Reasoning
Assistant**. Guides distinguish its history/LLM/report role from CT's image/CV/
measurement role and retain the existing `mhcra-*` contracts. No detector, weights,
training or schema changes are part of this documentation pass. Local checks for this pass: **81 tests passed in 23.90s**, Ruff/active-package
format passed, and all 25 maintained Markdown files passed local-target checks.
LOVISA passed 146 tests in 42.35s plus actual local gemma4:e2b smoke; the
ML-free contract/renderer/report still match exactly. Hosted results passed as recorded below.

### Hosted documentation release

[CT run 39929548618](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/39929548618)
passed for `281c2446d39736075d41aec74ceb9c9fb9002411`: Windows/Linux regression,
maintained-document links, actual pretrained/fixture bridges and Linux container.
[LOVISA run 39929551523](https://github.com/LilyC2024/Medical-AI/actions/runs/39929551523)
passed for `a37a716b7933a671532ef090781255929bbd1b97`: Python 3.10/3.12,
contract equality and actual fixture/pretrained/legacy transfers. This final
record changes documentation only; no GPU/patient-performance result is implied.

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

## LOVISA response-budget compatibility — 23 October 2026

The bridge adds an optional progress callback and fixed local CLI stage markers.
Existing exchange, model and review contracts are unchanged. All 81 regression
tests passed in 36.99s; 13 focused exchange tests passed in 4.31s after adding stage-order assertions.
The fixture regression checks both progress order and pending review. Existing dependency deprecation/tracing warnings remain.
Actual local fixture/pretrained CPU producer-receiver smokes completed in 1.65s /
12.43s using generated 32×64×64 input and no human approvals. GPU/NPU execution
and clinical accuracy remain untested. LOVISA owns its 110-second UI watchdog;
standalone CT training/full-volume processing retain their existing workflow.

[Hosted CT run 39938445818](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/39938445818)
passed at `5ba347cf6cd66b1931eaad3cd7d8cb27d4136606`: Windows/Linux regression,
actual pretrained inference/bridge and Linux container. The follow-up
verification record clarifies fixed viewer validation passes; code is unchanged.

[Hosted LOVISA run 39938918945](https://github.com/LilyC2024/Medical-AI/actions/runs/39938918945)
passed at `3c5e2d5e8a30c76c0cfda5f1925c740d004bbc5f`: Python 3.10/3.12 and actual
fixture/pretrained/legacy transfers against the pinned CT revision above.

## Final public-research publication checks

Tested producer `b73a72188efda899f9d0a0d321f905002bc7dac3` passed its [hosted workflow](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/40014638635). The CT workflow passed all configured jobs. The follow-up changes in this section and PLAN.md are documentation only. No datasets, weights, accounts or generated research-image reports were published.

## Publication and hosted verification — 24 October 2026

Tested source [9a3cdfe](https://github.com/LilyC2024/ai-medimg-2.5D-CT/commit/9a3cdfeb0dc71cb5a7e479e54d5a8430ddbe967c) is published.
[Hosted workflow 40099064726](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/40099064726)
completed successfully. Linux/Windows software checks, generated-data paths, CPU
container execution and actual official-weight phantom inference all passed.
LOVISA's joint workflow also passed against this exact producer pin.

Final follow-up changes only phase/evaluation Markdown records; tested runtime,
models, protocols and generated source references are unchanged. Local branch
and publication trees are checked for equality before synchronization.
