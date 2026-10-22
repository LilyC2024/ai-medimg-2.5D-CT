# Module, function and folder reference

[Overview](../../README.md) · [Architecture](architecture.md)

## New package: src/lung_nodule/

| Module / public API | Inputs, output and responsibility |
| --- | --- |
| [contracts.Record](../../src/lung_nodule/contracts.py) | Frozen Pydantic base; extra fields and nonfinite numeric values rejected |
| contracts.digest | Canonical JSON/model → SHA-256; consistency identity, not authentication |
| contracts.Geometry | Bounded source shape, spacing, origin and orthonormal LPS direction |
| Geometry.valid_geometry | Reject invalid dimensions, spacing, handedness and direction |
| Geometry.to_lps / from_lps | Source zyx voxel centers ↔ physical xyz LPS, including obliquity |
| contracts.SourceSlice | Ordered slice index, original byte hash, hashed SOP identity |
| contracts.Candidate / ordered_box | Local ID, score, six source-grid coordinates; positive extents required |
| contracts.ModelProvenance | Model/recipe/checkpoint identity, device, versions and fixture status |
| contracts.Study / consistent | Full source ordering, identity, bounds, unique candidates and threshold checks |
| contracts.Caliper.length_mm | Valid one-plane endpoints → physical length; rejects zero/outside distances |
| contracts.Decision | Accept/reject/uncertain plus optional reviewer caliper |
| contracts.Review.literal_booleans | Require literal human qualification and approval attestations |
| Review.verify | Bind digest, exactly one decision per candidate, no uncertainty and valid calipers |
| [sources.sha256](../../src/lung_nodule/sources.py) | Streaming local file digest |
| sources.load_sources | Approved series → HU, geometry, ordered evidence, source digest and input/protocol kinds |
| [phantom.generate_chest](../../src/lung_nodule/phantom.py) | New directory → generated DICOM and source marker; optional synthetic sphere |
| [detection.fetch_model](../../src/lung_nodule/detection.py) | Explicit pinned official setup download and artifact registration |
| detection.verify_model | Verify registration, recipe and every downloaded byte hash |
| detection.select_device | Explicit CPU/CUDA request; fail on unavailable device, never AUTO fallback |
| detection.build_detector | Construct upstream-compatible RetinaNet topology and selection/inferer settings |
| detection.prepare_tensor | HU/source affine → normalized RAS/resampled MetaTensor |
| detection.map_boxes | Transform eight corners to source AABBs and assign local candidate IDs |
| detection.MonaiDetector.__init__ / predict | Load verified tensor-only weights, execute offline inference, restore source boxes |
| detection.PhantomDetector.predict | Non-ML fixture component finder; never public research inference |
| detection.detect_study | Source loading + detector → validated Study and HU snapshot |
| [workspace.save_workspace](../../src/lung_nodule/workspace.py) | Create immutable-by-convention new study/pixel snapshot and integrity manifest |
| workspace.load_workspace | Validate identities, bounded NPY header/payload and pixel finiteness |
| workspace.overlay_slice | Source lung window with optional candidate rectangles and manual calipers |
| workspace.report_text | Valid study + review → deterministic evidence-linked research text |
| workspace.complete_review | Re-read workspace; compose report; persist explicit approval last |
| workspace.reviewed_report | Revalidate and regenerate on download; never trust report.md alone |
| workspace.export_synthetic_exchange | Reviewed generated workspace → separate versioned nodule ZIP; not MHCRA v1 |
| [cli.main](../../src/lung_nodule/cli.py) | fetch-model/demo/detect/review/export command parsing and dispatch |
| [ui.main](../../src/lung_nodule/ui.py) | Loopback Streamlit source viewer, candidate decisions, caliper preview and report download |
| [research.NoduleTruth / DatasetCase](../../src/lung_nodule/research.py) | Physical reference nodule; patient/study/split/image annotation records |
| DatasetManifest.group_separation | Enforce explicit approval, patient/hash separation, unique studies, relative paths and completeness |
| research.validate_dataset | Verify NIfTI bytes, affine, training spacing and truth-center bounds |
| research.prepare_training_image | Approved DICOM → source-preserving, resampled HU NIfTI; no labels/splits invented |
| research.launch_training | Explicit CUDA, verified upstream code, train/validation-only datalist and auditable run status |
| research.froc | Complete-volume one-to-one center-distance engineering FROC; not official challenge scorer |
| research.main | validate/prepare-image/train/evaluate CLI |

Helper scope is intentionally narrow: no generic plugin execution, arbitrary model
tool access, dynamic agents or cloud inference clients. Exceptions block the
affected operation; they do not silently replace input, models or approvals.

## Scripts

| File | Entry points and purpose |
| --- | --- |
| [smoke_lung.py](../../scripts/smoke_lung.py) | main: real local fixture/pretrained inference on generated CT; report must stay blocked |
| [lung_hardware.py](../../scripts/lung_hardware.py) | inspect_hardware/main: actual CUDA/OpenVINO inventory and technical JSON |
| [benchmark_lung.py](../../scripts/benchmark_lung.py) | main/run closure: unchanged-series full detection latency; load/first/warm measurements |
| [illustrate_lung.py](../../scripts/illustrate_lung.py) | main: reproduce source/box/caliper PNG from generated pixels |
| [check.py](../../scripts/check.py) | main: lint and full pytest suite, including legacy unittest classes |
| [check_docs.py](../../scripts/check_docs.py) | main: validate local Markdown links; external URLs/anchors not checked |

Legacy scripts/functions retain source docstrings and references in
[legacy pipeline](../legacy-pipeline.md). They are not new lung APIs.

## Repository folders

| Folder | Responsibility |
| --- | --- |
| src/lung_nodule | Active candidate, geometry, provenance, review, reporting and research modules |
| src/dicom_loader.py | Shared tested DICOM/HU/physical-order loader |
| third_party | Upstream Apache-2.0 license text retained for the adapted MONAI topology |
| src/data, src/models, src/baselines | Legacy 2.5D dataset/U-Net/teacher kept for reproducibility and v1 bridge |
| Other src modules | Legacy preprocessing, calibration, evaluation, privacy allowlist and visualization |
| deploy | Existing ONNX/CPU runtime, experimental API and synthetic MHCRA v1 producer |
| scripts | New reproducible commands plus retained legacy training/export/Intel tools |
| tests | New pytest functions plus legacy unittest regression classes; generated inputs only |
| configs | Legacy baseline configuration; active recipe is versioned in detection.py |
| reports | Safe technical evaluation evidence; old files are historical, not nodule metrics |
| docs/lung | Active detailed guides and this API map |
| docs/images | Generated illustrations; no patient images |
| metadata/examples | Legacy allowlisted technical example |
| data, data_processed, outputs | Ignored local inputs/results; only placeholders tracked |
| models, artifacts | Ignored local downloaded weights, registrations, runs and review workspaces |
| .github/workflows | CPU synthetic regression, compatibility, Docker and pretrained smoke CI |

For old reports, stored script hashes describe their historical commit; retired
source names are not promises of current commands. [Release/removal record](release.md).
