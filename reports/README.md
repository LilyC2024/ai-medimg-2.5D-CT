# Evidence inventory

Active lung evidence: [pretrained smoke](lung_pretrained_smoke.json) and
[CPU phantom latency](lung_cpu_latency.json), plus the
[evaluation record](../EVALUATION.md). The smoke uses generated pixels and proves
local execution/report blocking, not clinical detection accuracy.

All other existing JSON reports and windows-constraints.txt describe the earlier
head-region pseudo-label pipeline or its synthetic MHCRA v1 bridge. Their model,
input and commit hashes identify historical experiments. Do not transfer their
Dice, calibration, latency or Intel NPU results to the lung detector.

Local runs, actual reviewer records, weights and research images belong under
ignored artifacts/, models/ and data/, not in this public folder.
