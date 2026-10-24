# Contributing to the CT assistant

[Setup](docs/setup.md) · [Architecture](docs/lung/architecture.md) · [Security](SECURITY.md)

1. Read the active [phase](PLAN.md) and relevant current/legacy contract.
2. Reuse `.venv`; inspect versions before changing dependencies or device builds.
3. Reproduce a material defect with artificial data and a meaningful regression.
4. Keep source geometry, inference, review, exchange and interface separate.
5. Run [validation](docs/validation.md) and record executed/untested outcomes in
   [EVALUATION](EVALUATION.md). Real model execution is separate from scripted tests.
6. Update detailed linked guides and keep the root README short.

## Compatibility and research integrity

The ML-free `contracts.py`/`exchange_contract.py` are vendored into LOVISA with a
controlled import rewrite. Change producer and receiver intentionally, run exact
sync checks and both suites, then update LOVISA's tested producer pin. Keep old
synthetic-v2, research-v3 and legacy-v1 formats distinct; renaming a schema is not
a migration. Avoid introducing torch into LOVISA's lightweight environment.

Never infer absent acquisition dates, protocol, patient labels or negative truth.
Keep patient/hash-separated cohorts and audit pretrained overlap. No test success
promotes weights or establishes clinical accuracy. Record available hardware;
never claim CUDA/NPU execution that did not occur.

## AI-assisted development

AI coding agents write and review code under one human author. Agent reviews are
self-audits, not independent human, security or clinician review.

## Publication checklist

Review staged diff, changed interfaces, local links/anchors and full test results.
Exclude datasets, weights, original identifiers, local approvals and generated
clinical/research workspaces. Preserve MIT and third-party notices. State the
concrete bug, resulting behavior, validation and remaining assumptions. Publishing
source is not deployment or regulatory approval of a diagnostic service.
