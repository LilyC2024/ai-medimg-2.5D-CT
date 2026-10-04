# CT Project: Repair, Reproducibility, and Deployment TODO

Repository: https://github.com/LilyC2024/ai-medimg-2.5D-CT

Suggested repository filename: `TODO.md`.

Status date: 2026-10-04. Repairs and measured evidence are recorded in [docs/validation.md](docs/validation.md) and [reports/verification.json](reports/verification.json). Historical findings below describe commit `457ddbf70d65d62d0bfaa2589063ae8aceb00a23`, not the corrected pipeline. Checked items refer to implemented behavior and evidence; unchecked items remain incomplete or externally blocked.

## Completion audit

The corrected local pipeline produces 30 x 239 x 208 voxels, with 18 train / 4 validation / 4 test / 4 excluded buffer centers. All 30 required tests execute without skips; lint, a new environment/separate checkout synthetic workflow, relocated real-data evaluation, source-grid NPZ/NIfTI agreement, CPU ONNX parity and full-model NPU checks pass. See the validation table for evidence by requirement. The target namespace restructuring is deliberately deferred because installed existing modules work.

Open requirements are explicit:

- Historical exact Windows commands were unavailable; baseline HEAD/status/versions and available command names are recorded without invented history.
- Real-data source URL, acquisition terms and redistribution rights remain unknown. Original-file hashes stay local, and real overlays/models are not distributed.
- Docker is unavailable locally. Hosted Linux CI built and ran the CPU image successfully; hosted Windows/Linux lint and regression tests passed.
- Reviewable repair commits exist. The repair branch was pushed and remote HEAD verified; a release tag is withheld while acquisition/rights and release gates remain open.
- The clinical task is proposed only. Expert annotated multi-patient data, independent clinical evaluation, matched alternatives and a clinical product programme require external data and domain review.

## 1. Intended Outcome and Scope

Deliver an externally reviewable research prototype that can ingest a supported CT DICOM series, validate geometry and HU conversion, preprocess it, generate explicitly identified pseudo labels, train a compact PyTorch 2.5D U-Net, evaluate it reproducibly, export ONNX, and run verified CPU and Intel NPU inference.

The current task is agreement with classical head-region pseudo labels. It is not lesion diagnosis, expert-annotated anatomical segmentation, or demonstrated clinical accuracy. A clinically meaningful segmentation claim requires a defined target, multiple patients, suitable expert annotations, and an independent evaluation. Keep that extension separate from the engineering prototype.

Completion means a reviewer can understand the limitations, acquire permitted data, execute documented commands from a clean checkout, inspect machine-readable evidence, and distinguish completed experiments from planned work.

## 2. Current Evidence

| Area | Observed status | Remaining gap |
| --- | --- | --- |
| Windows development | Python 3.12.1; PyTorch 2.14.1+cpu; imports and CPU backward pass succeeded | Record project-specific dependencies and reproduce in a fresh environment |
| Hardware | Core Ultra 7 155U; approximately 32 GB RAM; Intel AI Boost driver 32.0.100.5540 | Measure complete CT model execution |
| OpenVINO | Version 2026.3.1; CPU/GPU/NPU visible | Visibility alone is not model validation |
| NPU smoke test | Convolution executed on NPU; mean/max CPU difference 2.80e-05 / 4.33e-04 | No full U-Net NPU result yet |
| Raw CT | Locally restored; 34 slices, 512 x 512; spacing z/y/x = 5 / 0.488281 / 0.488281 mm | Acquisition source, redistribution rights, file manifest and pixel-padding checks |
| Preprocessing | 34 x 250 x 250 after resampling; 29 x 207 x 171 after crop; spacing 5 / 1 / 1 mm | Full geometry and inverse mapping validation |
| Pseudo labels | 29 slice NPZ files and overlays generated; no built-in quality flags | Visual review and label contract; flags are not clinical validation |
| Local index | Regenerated under data_processed/windows_check; loader completed | Full path-reference check and corrected split isolation |
| GitHub snapshot | README claimed bundled DICOM; actual raw data absent; tracked index used old absolute paths | Correct acquisition and clean-checkout workflow |
| Model artifact | best.pt exists locally, 1,963,305 bytes | Safe loading, provenance, matching architecture and input contract |
| Push status | User requested pushes | Successful push of both repositories has not been confirmed |

The raw 34-slice versus processed 29-slice difference is explained by the crop: z bounds [2,31), y [24,231), x [36,207). It is not evidence of five missing source slices. The matching series UID supports a shared series origin; complete file identity has not been established.

## 3. Priority and Execution Order

| Priority | Meaning |
| --- | --- |
| P0 | Correctness or reproducibility blocker; required before publishing new performance claims |
| P1 | Required for a complete engineering release |
| P2 | Research or product extension after the reproducible baseline |

Order: baseline preservation -> data contract -> ingestion/geometry -> split repair -> training/evaluation -> ONNX CPU -> NPU -> service -> documentation/cleanup -> release.

Within the three-day portfolio plan, Day 1 covers the CT P0 subset that fits measured time. Days 2-3 remain allocated to endoscopy. Do not silently treat this complete backlog as one day's work. Finish unresolved CT items after the sprint and label them open.

## 4. Baseline Preservation and Requirements — P0

- [ ] Record HEAD, Git status, Python/package versions, and the exact commands already used on Windows.
- [x] Create a dedicated repair branch; preserve historical results in Git history before restructuring.
- [x] Define intended input, output classes, users, research purpose, supported DICOM types, and unsupported inputs.
- [x] Define success criteria for loading, geometry, split isolation, model evaluation, runtime parity, and deployment.
- [x] Create a short requirements-to-evidence table in `docs/validation.md`; every completed requirement links to a test or report.
- [x] Treat old checkpoint/report results as historical until regenerated against corrected data and code.

Acceptance: scope and input/output contract are explicit; baseline is recoverable; no new result mixes old and repaired pipelines.

## 5. Data, Metadata, and Git Policy — P0

### 5.1 Publish small metadata deliberately

Small metadata is appropriate for direct Git commits after sanitization. File size is not a privacy or redistribution criterion. Do not publish raw DICOM headers wholesale.

| Item | Repository policy |
| --- | --- |
| Sanitized technical JSON | Commit shape, spacing, orientation, rescale ranges, crop transform, configuration and quality checks |
| Data/split manifests | Commit stable case aliases, relative references, split assignments, permitted checksums and schema version |
| Metric/benchmark JSON or CSV | Commit compact reproducible evidence with run and model identifiers |
| Patient/study identifiers, dates, institution text, private tags | Exclude unless specifically reviewed and justified; use synthetic aliases for public reports |
| Original DICOM UIDs | Omit or replace consistently in public metadata; keep any mapping local |
| Usernames and machine-specific paths | Replace with relative paths or named data-root references |
| Raw DICOM and derived images/masks | Keep local or provide permitted external acquisition; publish only if rights and disclosure review allow it |
| Checkpoints, ONNX and runtime caches | Ignore by default; distribute selected versioned models through release assets if permitted |

- [ ] Document dataset provenance, source URL, acquisition instructions, licensing/terms, expected files, and permitted uses in `docs/data.md`.
- [x] Establish a public technical-metadata allowlist; a field not on it is excluded by default.
- [x] Replace the current raw series UID and old `C:\\AI\\...` references in public examples with a stable case alias and relative references.
- [x] Create `metadata/examples/sample_001.json` containing only reviewed technical fields.
- [x] Add metadata schema validation and a check for machine-specific paths and prohibited identifying fields.
- [x] Keep originals local; do not describe alias replacement alone as full DICOM anonymization.
- [x] Review screenshots and image overlays separately for identifying text and redistribution permission.
- [x] Move the stale tracked index to an explicitly sanitized historical example, or remove it after replacing it with a valid reproducible manifest.
- [x] Resolve all manifest references relative to a configurable data root, never the shell's accidental working directory.
- [ ] Provide a source-file manifest and checksums where publication is permitted; never use a hash alone as evidence of anonymization.

Acceptance: a fresh clone contains useful small metadata without local paths or unreviewed identifiers; the README accurately states whether image data is bundled.

### 5.2 Fixtures versus real data

- [x] Add a tiny synthetic DICOM fixture generator for automated tests, including rescale and geometric metadata.
- [x] Make a clean-checkout synthetic end-to-end test possible without private or external files.
- [x] Keep a separate real-data reproduction command that reports missing data with actionable instructions.

Acceptance: synthetic CI proves software behavior; real-data results remain separately identified.

## 6. DICOM Ingestion, HU, and Geometry — P0/P1

- [x] Validate modality, series membership, dimensions, orientation, pixel spacing, slice positions and decoding support.
- [x] Sort slices by projection of ImagePositionPatient onto the slice normal derived from ImageOrientationPatient. Reject or explicitly handle inconsistent orientations.
- [x] Define policies for duplicate positions, nonuniform spacing, mixed series, missing tags, localizers, and multi-frame DICOM. Unsupported cases must fail clearly.
- [x] Verify HU conversion is applied exactly once across pydicom and SimpleITK paths, including compressed transfer syntax fixtures. Audit the suspected rescale risk rather than declaring it a proven bug.
- [x] Investigate minimum HU -4048 against stored pixels, PixelPaddingValue/RangeLimit and decoding behavior. Exclude padding from relevant intensity statistics and ROI logic where appropriate.
- [x] Preserve physical origin, direction and spacing through preprocessing and export. Array shape plus spacing is insufficient.
- [x] Save forward/inverse transforms for resampling, crop and model resize; document inclusive/exclusive bounds.
- [x] Restore predictions onto the source image grid with nearest-neighbor label interpolation; verify physical landmarks and voxel alignment.
- [x] Document why coarse 5 mm z spacing is retained; do not equate interpolated slices with new anatomical information.

Acceptance: synthetic axial/oblique cases, rescale-once checks, and prediction geometry round trips pass; the real sample has a reproducible ingestion report.

## 7. Pseudo Labels and 2.5D Data Contract — P0

- [x] Define the four classes precisely, including how brain-like, bone and overlap labels are assigned. Avoid asserting anatomical ground truth.
- [x] Version pseudo-label generation parameters; save method, thresholds, morphology and preprocessing fingerprint.
- [x] Review representative overlays across z, including crop extremes and failures. Record observations, not just the absence of flags.
- [x] Ensure volume, labels and index share case alias, shape, geometry, preprocessing version and checksum references.
- [x] Document the 2.5D tensor as ordered neighboring slices, boundary handling, normalization, resize and label interpolation.
- [x] Verify all indexed file references exist and reject malformed rows before training.

Acceptance: labels and inputs have a shared, validated contract; pseudo-label agreement is explicitly distinguished from clinical accuracy.

## 8. Split Repair and Leakage Tests — P0

The earlier audit found overlapping raw input slices across the existing split boundaries. A one-slice buffer between center slices is insufficient for radius-1 stacks.

- [x] For every sample, compute the complete raw-slice support used by its 2.5D stack.
- [x] Assert pairwise-disjoint support across train/validation/test, including boundary clamping and any additional context.
- [x] For radius-1 stacks, require centers across split boundaries to differ by at least three slices; use discarded centers/bands accordingly and verify by support sets rather than a magic buffer count.
- [x] Group all series from one patient into one split when patient identity is available. The current patient-plus-series key is not patient isolation.
- [x] For the current single-series sample, use a documented contiguous demonstration split; state that it cannot establish generalization to unseen patients.
- [x] Do not silently substitute training data when validation or test data is absent. Fail or select an explicitly labeled training-only mode.
- [x] Freeze and checksum the split manifest before training. Record excluded buffer samples.
- [x] Add a regression test reproducing the earlier leakage and proving the new partition has no shared input support.

Acceptance: zero cross-split support overlap, explicit subject limitations, and no training-set fallback in held-out reports.

## 9. Architecture and Training — P0/P1

- [x] Document the implemented compact U-Net: 3 input channels, 4 output classes, base width, encoder/decoder blocks, skip connections and parameter count.
- [x] Remove unsupported claims of substantive MONAI usage. Retain MONAI only if it has a specific implemented role.
- [x] Add a single validated training configuration for seed, optimizer, learning rate, batch size, epochs, image size, augmentation, loss and checkpoint selection.
- [x] Make augmentation reproducible but variable across epochs; the earlier fixed per-sample seed can repeat transformations indefinitely.
- [x] Keep spatial transformations synchronized between input stacks and labels.
- [x] Record train/validation losses and classwise metrics, elapsed time, data version and Git commit for each run.
- [x] Save checkpoint architecture, preprocessing contract and selection criterion, plus provenance and artifact checksum.
- [x] Verify best.pt loading against the implemented architecture; inspect metadata safely before allowing any compatibility fallback that loads arbitrary pickle objects.
- [x] Retrain a corrected baseline after split/inference repair. Do not reuse the old metrics as repaired results.
- [x] Measure a short CPU training run before selecting the final epoch and batch budget.

Acceptance: one configuration reproduces a run; a checkpoint can be traced to its data and code; augmentation and held-out selection behave as documented.

## 10. Evaluation, Calibration, and Case Analysis — P0/P1

- [x] Evaluate only the requested split; remove accidental evaluation over mixed train/validation/test rows.
- [x] Assemble predictions by case/series in physical slice order before any 3D postprocessing. Current CSV split ordering and batch-local postprocessing can mix nonadjacent slices.
- [x] Verify prediction/metric invariance to inference batch size, within declared numerical tolerances.
- [x] Report per-class Dice/IoU, foreground summary, sample counts and aggregation method. Define empty-class handling explicitly instead of awarding automatic perfect scores.
- [x] Use volume-level or correctly accumulated confusion statistics rather than uncontrolled averages of batch metrics.
- [x] Compare the classical teacher, raw network output and postprocessed network output under the same split and geometry.
- [x] Explain that agreement with the teacher cannot establish superiority over that teacher without independent expert labels.
- [x] Add failure cases: crop failures, small classes, boundary slices, class confusion and preprocessing sensitivity.
- [x] Investigate the old temperature-scaling result: ECE improved but NLL worsened. Do not claim successful calibration from ECE alone.
- [x] Use separate calibration data where feasible; with this tiny sample, report calibration as exploratory or omit it from the primary baseline.
- [x] Guard calibration optimization failures and retain identity temperature when the selected fitting objective worsens on the fitting set; assess calibration generalization separately.
- [x] Reserve test data from threshold, temperature, model and postprocessing selection.
- [x] Label uncertainty maps as model behavior summaries, not validated clinical confidence.

Acceptance: reports distinguish splits and pseudo-label limitations; ordering/batch regression tests pass; every published number points to an actual result artifact.

## 11. ONNX and CPU Deployment — P0/P1

- [x] Export the verified checkpoint with an explicit input/output contract, exporter version and opset.
- [x] Choose fixed [1,3,256,256] deployment input initially if it matches the checkpoint contract; explain any resize and inverse transform. Do not change checkpoint assumptions silently.
- [x] Validate the graph and test multiple representative and boundary stacks against PyTorch.
- [x] Make parity failure return a nonzero exit status; do not limit validation to one convenient batch.
- [x] Start with CPU probability tolerance atol=1e-4, rtol=1e-3 and mask agreement >=99.9% as provisional engineering gates; document exceptions and near-tie behavior before changing gates.
- [x] Explicitly select CPUExecutionProvider for the ONNX Runtime CPU baseline.
- [x] Reuse a runtime session; avoid repeated checkpoint loading and model session creation per request.
- [x] Verify CLI determinism, output class IDs, restored geometry and output-file content.
- [ ] Publish selected ONNX/checkpoint release assets with checksums and provenance when permitted; do not promise artifacts that are absent.

Acceptance: a documented CLI creates a valid mask from permitted input and fails clearly on invalid input; CPU parity evidence is committed.

## 12. Intel NPU and Performance Validation — P1

- [x] Compile the full U-Net on the actual 155U NPU early; record compiler errors and unsupported operations.
- [x] Explicitly select NPU, record EXECUTION_DEVICES, and report any mixed execution or fallback. Do not infer execution from Task Manager alone.
- [x] Compare PyTorch CPU, ONNX Runtime CPU, OpenVINO CPU and OpenVINO NPU on identical preprocessed inputs.
- [x] Document runtime precision and tensor differences. Evaluate labels and held-out segmentation metrics after numerical comparison.
- [x] Use a provisional absolute Dice drop <=0.01 as an engineering investigation threshold, not a clinical acceptance criterion; define tolerances before evaluating.
- [x] Measure compilation/first inference separately from warm inference; document caching behavior.
- [x] Measure warm-up plus repeated runs with p50/p95 latency, throughput, sample count, thread/request settings and memory.
- [x] Measure end-to-end latency separately: DICOM read, preprocessing, stack creation, inference, postprocessing and export.
- [x] Record power mode, plugged-in state, software versions and model checksum; include performance regressions or absent speedup honestly.
- [x] Keep optional Intel GPU testing separate from the required CPU/NPU comparison.

Acceptance: the full-model NPU result is reproducible, with actual device evidence and comparable quality/latency data. The convolution smoke test is never presented as U-Net validation.

## 13. Service and Packaging — P1

- [x] Make CLI the primary validated deployment path. If API cannot be completed, mark it experimental and remove unsupported production claims.
- [x] Provide useful response artifacts: downloadable mask plus sanitized technical metadata, not inaccessible server-local paths.
- [x] Bound upload size and supported dimensions, validate archive extraction paths, reject ambiguous series, and clean temporary files on success/failure.
- [x] Initialize the model once; make readiness reflect successful model initialization rather than unconditional OK.
- [x] Bind local examples to 127.0.0.1 by default; avoid logging identifying DICOM fields.
- [x] Test one valid request, malformed/oversized inputs, and unavailable model behavior.
- [x] Provide a reproducible CPU Docker image only after the CLI works; document NPU deployment separately on Windows. Do not promise NPU passthrough in the CPU container.

Acceptance: documented input limits and outputs match actual behavior; failed requests do not leave accumulating temporary data.

## 14. Target Repository Structure and Documentation — P1

Use this as a destination, not a requirement to rewrite working code before P0 fixes.

| Path | Purpose |
| --- | --- |
| README.md | Scope, actual status, verified quickstart, results and limitations |
| TODO.md | This backlog and evidence links |
| pyproject.toml | Authoritative package metadata and dependency groups |
| configs/ | Training and deployment configurations |
| src/ct25d/ | Importable ingestion, preprocessing, labels, data, model, evaluation and runtime modules |
| scripts/ | Thin command-line wrappers |
| deploy/ | CLI/service adapters only where useful |
| tests/ | Synthetic fixtures and correctness regression tests |
| metadata/ | Sanitized examples and reviewed manifests |
| docs/ | Data, architecture, reproduction, validation, model card and regulatory scope |
| reports/ | Selected small evaluation and benchmark evidence |
| artifacts/ | Ignored local model and runtime outputs |

- [x] Consolidate documentation into data.md, architecture.md, reproducibility.md, validation.md, model_card.md and regulatory_scope.md.
- [x] Explain the model, pseudo-label task, 2.5D rationale, data flow, geometry, split limitations and runtime choices.
- [x] Provide a tested Windows quickstart using the selected Python executable; include data acquisition before preprocessing.
- [x] Specify every command's inputs, outputs, expected success signal and prerequisites.
- [x] Clearly separate synthetic smoke tests, real-data reproduction, training and deployment.
- [x] Record actual AI-agent assistance and human verification; do not invent tool usage or experiments.
- [x] Include a preliminary EU MDR scope discussion: intended purpose drives qualification/classification; diagnostic decision-support may fall under Rule 11, with severity determining class. State that this research prototype has no CE claim.
- [x] Link current official regulatory guidance and distinguish a research backlog from a clinical product/CE programme.
- [x] Align package version, README, release notes and model version; remove conflicting 0.7 versus 1.0 status claims.
- [x] Choose an appropriate code license and add attribution; clarify that it does not license source data or third-party model assets.

Acceptance: an unfamiliar reviewer can follow the project without the original sprint conversation or old machine paths.

## 15. Cleanup: Retain, Consolidate, Remove — P1

Delete redundant items only after a replacement is verified. Preserve useful history through Git, rather than retaining multiple competing implementations in the active tree.

| Candidate | Action | Required check |
| --- | --- | --- |
| Raw data, volumes, masks and temporary Windows outputs | Keep locally and ignore; remove from Git tracking if tracked | Provenance and reproduction instructions exist |
| Stale absolute-path index | Replace or remove from active quickstart | New manifest works from a different root |
| Duplicate day-by-day docs | Consolidate; retain a short dated journal if useful | Unique technical content migrated and links updated |
| Interview notes | Move useful facts to public docs; remove irrelevant coaching content from active tree | No unique evidence lost |
| Old release notes and summary | Rewrite as clearly historical or consolidate | No contradictory version/results remain |
| Repeated inference/preprocessing code | Consolidate into tested shared modules | CLI/training outputs preserve intended behavior |
| Unused dependencies, including MONAI if unused | Remove from package and install files | Imports, tests and documented commands pass |
| Duplicate dependency lists | Use pyproject plus reproducible environment/constraints instructions | Clean installation works; CPU wheel source is documented |
| Tracked checkpoints and plots | Keep only selected justified examples; move distributable models to release assets | Downloads and provenance are valid |
| sys.path hacks | Replace through proper packaging as modules migrate | Scripts run from installed package |
| Tests that always skip missing data/model | Replace core coverage with synthetic tests; keep explicit optional integration tests | CI shows executed tests, not an all-skip success |
| Local editor settings | Remove machine paths; retain only portable useful settings | Fresh VS Code setup remains documented |
| Obsolete scripts/placeholders and generated caches | Delete after reference search and replacement verification | No live imports, docs or workflow references |

- [x] Build a cleanup inventory with path, reason, replacement and verification result.
- [x] Search references before each deletion; review imports, entry points, Docker and documentation together.
- [x] Remove shared logic duplication before removing wrappers that users still need.
- [x] Update .gitignore and inspect staged files explicitly; avoid broad staging of local data.
- [x] Do not delete source datasets, the only recoverable checkpoint, or backup evidence as routine cleanup.
- [x] Do not rewrite Git history as part of ordinary cleanup. Investigate separately if sensitive content was previously committed; a normal deletion does not erase history.

Acceptance: the active tree has one clear implementation path, no stale claims or broken links, and no unrelated local files in the release commit.

## 16. Verification and Release — P0/P1

- [x] Run meaningful regression tests for split isolation, geometry, HU conversion, ordering, empty-class metrics and runtime parity.
- [x] Add CI with synthetic CPU tests and linting; NPU hardware testing remains a separately recorded local job.
- [x] Ensure required tests cannot silently pass through missing-fixture skips.
- [x] Reproduce installation and the synthetic workflow in a new directory/environment.
- [x] Run the real-data pipeline under a different data root to expose absolute-path assumptions.
- [x] Validate JSON/CSV schemas, documentation links and the exact README commands.
- [x] Inspect the staged diff for identifying fields, local paths, unexpected binaries and generated files.
- [ ] Commit repairs in reviewable units; push the branch, verify remote HEAD and tag a release only after gates pass.
- [x] Publish concise release notes: changed behavior, reproducible evidence, known limitations and unresolved TODOs.

Release gates: no split-support overlap; no mixed-split primary metrics; valid geometry restoration; successful synthetic CI; reproducible CPU inference; truthful artifact availability; documented full-model NPU outcome; reviewed public metadata.

## 17. P2: Clinical and Research Extension

- [ ] Choose one clinically meaningful segmentation task and justify clinical workflow, users and failure consequences.
- [ ] Acquire a permitted multi-patient dataset with expert labels and an annotation/quality protocol.
- [ ] Split by patient, assess site/scanner variation and plan external validation.
- [ ] Compare the compact baseline with appropriate alternatives under matched data and compute budgets.
- [ ] Assess clinical evaluation, risk management, software lifecycle, usability, cybersecurity and post-market requirements before any clinical product claim.

These items are outside a one-day CT repair and outside proof supplied by this single-series prototype.

## 18. Practical Day 1 Checklist

- [x] Preserve baseline and correct README/data availability claims.
- [x] Commit reviewed technical metadata and a data acquisition contract.
- [x] Complete path validation and fix split support leakage with a regression test.
- [x] Fix series ordering and volume-level postprocessing; remove training-data evaluation fallback.
- [x] Run corrected evaluation or explicitly mark it pending if retraining cannot finish.
- [x] Verify checkpoint loading, ONNX CPU parity and attempt full-model NPU compilation.
- [x] Commit a concise report of what actually passed and what remains open.

Do not spend Day 1 deleting documentation or reorganizing the entire package while correctness blockers remain. Complete cleanup after replacements are validated.

## References for Implementation

- DICOM confidentiality profile and options: https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_E.html
- OpenVINO NPU device behavior: https://docs.openvino.ai/2026/openvino-workflow/running-inference/inference-devices-and-modes/npu-device.html
- PyTorch ONNX export: https://docs.pytorch.org/docs/stable/onnx.html
- ONNX Runtime execution providers: https://onnxruntime.ai/docs/execution-providers/

Check current vendor compatibility and regulatory guidance during implementation. These references do not turn the prototype into a clinically validated or CE-certified product.
