# CT validation: current checks and historical evidence

[Overview](../README.md) · [Actual results](../EVALUATION.md)

## Current software checks

```bash
.venv/bin/python scripts/check.py
.venv/bin/python scripts/smoke_lung.py --output artifacts/fixture-smoke.json
.venv/bin/python scripts/smoke_lung.py --model-dir models/luna16 --device cpu --output artifacts/pretrained-smoke.json
```

`check.py` runs documentation links, Ruff and the full pytest suite. Inputs are
synthetic; test review identities are scripted. The real pretrained smoke is
separate, requires installed verified weights and leaves report approval blocked.
Windows/Linux CI also exercises both bridge commands; Linux checks Docker. LOVISA
runs its own regression and pinned real producer-consumer smokes.

## Evidence map

| Requirement | Source |
| --- | --- |
| Current source, geometry, detection, review and exchange | [tests](../tests) and [current evaluation](../EVALUATION.md) |
| Actual pretrained CPU inference on generated CT | [Smoke JSON](../reports/lung_pretrained_smoke.json) |
| Phantom CPU latency | [Latency JSON](../reports/lung_cpu_latency.json) |
| Legacy rescale/padding/geometry | [Repair tests](../tests/test_repairs.py), [HU investigation](../reports/hu_investigation.json) |
| Legacy frozen split and training trace | [Data manifest](../reports/data_manifest.json), [training](../reports/training.json) |
| Legacy held-out metrics/batch invariance | [Evaluation](../reports/evaluation.json), [invariance](../reports/invariance.json) |
| Legacy ONNX provenance/parity | [Parity](../reports/onnx_parity.json), [deployment](../reports/deployment.json) |
| Actual historical full U-Net Intel NPU | [Benchmark](../reports/intel_benchmark.json) |
| Historical fresh environment/checkout/container | [Verification](../reports/verification.json) |
| LOVISA synthetic legacy bridge | [Integration record](../reports/mhcra_integration.json) |

## Interpretation limits

Generated-pixel success establishes software execution, not sensitivity, clinical
utility or safety. Current CUDA training/new-detector NPU execution and independent
patient evaluation remain unexecuted. Legacy metrics compare heuristic labels on
one series; raw and worse postprocessed results stay separate. Empty-class/global
metric rules are in [legacy architecture](architecture.md).

The historical real sample's rights/source remain unresolved. Numeric aliases and
hashes do not establish anonymization. No patient/model asset release is implied.
[Data](data.md) · [Scope](regulatory_scope.md).
