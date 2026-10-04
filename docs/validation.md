# Requirements to evidence

The baseline is recoverable at commit 457ddbf. Corrected training is traced to its exact code commit, frozen split and data hashes in reports/training.json; subsequent runtime validation commits are separate. Checked tasks in CT_Project_TODO.md refer to this table and its linked reports. Synthetic tests prove software behavior, not clinical accuracy.

| Requirement | Evidence | Acceptance/status |
| --- | --- | --- |
| Scope, supported input and four outputs | [architecture.md](architecture.md), [data.md](data.md), [model_card.md](model_card.md) | Explicit research and pseudo-label contract |
| Safe public technical metadata | [../metadata/examples/sample_001.json](../metadata/examples/sample_001.json), [../src/public_metadata.py](../src/public_metadata.py), [../tests/test_repairs.py](../tests/test_repairs.py) | Allowlist and machine-path/prohibited-field rejection |
| Rescale once, padding, axial/oblique/compressed geometry | [../tests/test_repairs.py](../tests/test_repairs.py), [../reports/hu_investigation.json](../reports/hu_investigation.json) | Synthetic RLE and real independent JPEG/SimpleITK comparison |
| Physical transform and source-grid restoration | [../tests/test_repairs.py](../tests/test_repairs.py), [../tests/test_e2e_smoke.py](../tests/test_e2e_smoke.py), [../reports/deployment.json](../reports/deployment.json) | Source origin/direction/spacing and nearest inverse labels |
| No cross-split direct stack support | [../tests/test_repairs.py](../tests/test_repairs.py), [../reports/data_manifest.json](../reports/data_manifest.json) | Frozen contiguous demonstration, two excluded centers per boundary |
| No missing held-out fallback | [../scripts/train.py](../scripts/train.py), [../scripts/infer.py](../scripts/infer.py) | Nonempty explicit splits required; multi-series patient leakage rejected |
| Reproducible epoch augmentation and synchronized masks | [../tests/test_ct25d_dataset.py](../tests/test_ct25d_dataset.py), [../tests/test_repairs.py](../tests/test_repairs.py) | Same seed/epoch reproduces; changing epoch varies transformations |
| Traceable training and safe checkpoint | [../reports/training.json](../reports/training.json), [architecture.md](architecture.md) | Architecture/state checked, data/config/source hashes, no pickle fallback |
| Split-only ordered volume evaluation | [../reports/evaluation.json](../reports/evaluation.json), [../reports/invariance.json](../reports/invariance.json) | Test only, global class statistics, identical masks across batches 1/2/3 |
| CPU ONNX graph/parity and provenance binding | [../reports/onnx_parity.json](../reports/onnx_parity.json), [../tests/test_repairs.py](../tests/test_repairs.py) | Declared probability/mask gates; mismatched ONNX or preprocessing fails |
| Full U-Net Intel CPU/NPU | [../reports/intel_benchmark.json](../reports/intel_benchmark.json) | Explicit NPU-only execution; FP16 quality gate distinct from FP32 CPU gate |
| Real CPU CLI source output and determinism | [../reports/deployment.json](../reports/deployment.json), [../reports/invariance.json](../reports/invariance.json) | Source shape, class IDs, artifact content and restored geometry |
| Bounded service with reusable initialized runtime | [../tests/test_service.py](../tests/test_service.py), [reproducibility.md](reproducibility.md) | Valid/malformed/oversized/unavailable behavior; cleanup; downloadable artifacts |
| Fresh environment and separate checkout | [../reports/verification.json](../reports/verification.json) | Required tests/lint and synthetic generation→training→export→CLI execute |
| Small reports and repository cleanup | [cleanup.md](cleanup.md), [../reports/baseline.json](../reports/baseline.json) | Data/models retained locally and ignored; no public images or source headers |
| CPU CI | [../.github/workflows/ci.yml](../.github/workflows/ci.yml) | Windows/Linux lint and tests passed: [hosted CI](https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/37233373549) |
| Real-data acquisition and rights | [data.md](data.md) | OPEN: source URL/terms not supplied; no real download or redistribution promised |
| CPU container build | ../Dockerfile, [reproducibility.md](reproducibility.md) | PASS: hosted Linux CI built the CPU image and verified synthetic source-grid inference; Docker is unavailable locally |
| Clinical generalization and CE programme | [regulatory_scope.md](regulatory_scope.md) | OPEN: no expert multi-patient data or independent clinical validation |

Global Dice/IoU aggregate voxel statistics per class before an unweighted foreground mean. Both-empty classes are null/excluded and an all-empty foreground summary is zero. The teacher's self-agreement is tautological. Raw and postprocessed scores are reported separately; the current postprocessor worsens agreement and remains unchanged to avoid test-set tuning. Primary calibration is identity; old NLL worsening despite ECE improvement is documented as a failure, not successful calibration. Uncertainty is not clinical confidence.

Application model caches are disabled; driver caches were not reset, so reported compilation may be warm. Peak memory is cumulative process working set, not device RAM. Runtime latency reflects this machine and recorded settings, not a universal speedup or clinical acceptance gate.

No tagged release or public patient/model asset distribution is approved while acquisition/rights and other release gates remain open. Git history was not rewritten; a separate history/disclosure review may be needed for previously committed identifiers. Source-file hashes remain local pending publication permission.
