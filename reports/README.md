# Recorded technical evidence

[Current evaluation](../EVALUATION.md) separates software checks from clinical
performance. [lung_pretrained_smoke.json](lung_pretrained_smoke.json) records actual
local pretrained inference on generated CT and blocked unapproved reporting.
[lung_cpu_latency.json](lung_cpu_latency.json) records phantom CPU latency, not
full-scan clinical reading time.

Other existing JSON records describe the legacy 2.5D head-region pseudo-label or
synthetic tissue-mask integration experiments. Their input/model/commit hashes
identify those historical runs. Do not apply legacy Dice, calibration or Intel
NPU results to the current lung detector. [Legacy evidence guide](../docs/validation.md).

Commit no new patient images, local approvals, reviewer identities or weights here.
Keep local runs under ignored `artifacts/`, `models/` and `data/`.

The 24 October audit adds software regressions and separately measured local
smokes, recorded in [EVALUATION](../EVALUATION.md). It does not reinterpret older
clinical/sample permissions or add a new benchmark. Every new record should state
input scope, model/config/source identity, backend, timing scope, review status and
whether inference was actual or scripted. Real pixels and weights remain ignored.
