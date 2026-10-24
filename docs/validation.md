# Validate CT software and interoperability

[Overview](../README.md) · [Actual outcomes](../EVALUATION.md) · [Expert repairs](review.md)

## Local software checks

Run from the CT checkout in its existing environment:

```bash
.venv/bin/python -m pip check
.venv/bin/python -m compileall -q src deploy scripts tests
.venv/bin/python -m ruff check src scripts deploy tests
.venv/bin/python -m ruff check src/lung_nodule --select F
.venv/bin/python -m ruff format --check src/lung_nodule
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_docs.py
```

[Tests](../tests) cover source ordering/geometry/identity, mapping and calipers,
review/content binding, hostile exchange archives, source/header allocation,
patient/hash leakage, and retained 2.5D/API behavior. New review regressions cover
upload cleanup ownership, duplicate/encrypted members, fractional targets,
nonfinite/complex HU and retryable workspace validation. Scripted detector tests
are labelled software checks, not actual pretrained inference.

The Markdown checker checks local files and heading anchors, including repeated
headings, encoded paths and fenced examples. It does not contact external URLs.

## Actual local detector checks

```bash
# Non-ML generated phantom
.venv/bin/python scripts/smoke_lung.py --output artifacts/fixture-smoke.json
# Actual registered pretrained weights on generated pixels
.venv/bin/python scripts/smoke_lung.py --model-dir models/luna16 --device cpu --output artifacts/pretrained-smoke.json
```

Use the installed registered model directory; this host may use `models/luna16-full`.
Both smokes leave review pending. No candidate count is an accuracy metric.
[Public ROI reproduction](lung/public-demo.md) is a separate research smoke with
pretrained-overlap and annotation-selection limitations.

## LOVISA joint checks

In LOVISA's own `.venv`, run exact CT contract sync and its fixture/pretrained/
legacy producer-consumer smokes. The receiver independently validates bounded
HU, geometry, previews, candidates and pending review; no smoke should issue an
actual-app approval. See [receiver validation](https://github.com/LilyC2024/Medical-AI/blob/main/docs/VALIDATION.md).

## Hosted and hardware boundaries

Linux/Windows CI exercises generated data, actual tiny legacy training/export,
CPU container paths and a pinned official-weight phantom smoke. Setup downloads
are explicit; no public patient cohort or clinician report is uploaded. CUDA
training and Intel NPU execution require actual hardware and separate evidence.
Record warnings/failures honestly in EVALUATION; passing software tests is not
clinical, regulatory or independent model validation.
