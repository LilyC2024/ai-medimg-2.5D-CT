# CT implementation and verification phases

Complete/test each phase before beginning another. Software checks do not establish
clinical accuracy or actual accelerator execution. [Evidence](EVALUATION.md).

| Phase | Deliverable | Completed evidence |
| --- | --- | --- |
| Foundation | Preserve legacy paths; add geometry/source/candidate/review contracts and phantom | 32 legacy + 6 new foundation tests |
| Detection | Verified offline MONAI detector, explicit device, source mapping | 10 cumulative nodule tests; actual official-weight CPU phantom inference |
| Review | Source/candidate UI, calipers, approval and canonical report | 20 cumulative nodule checks including AppTest/tamper/stale approval |
| Research/deployment | Patient/hash-separated manifests, FROC, CUDA launcher and hardware inventory | 29 cumulative checks; actual CUDA/NPU unavailable and not marked passed |
| Initial publication | Portable docs/code, actual smokes and hosted release | 68 tests; Windows/Linux, pretrained smoke and Linux Docker passed |
| Nodule producer | Shared ML-free nodule-v2, HU/all-slice previews and pending bridge | 26 producer/review checks |
| LOVISA consumer/joint release | Authenticated candidate/caliper acceptance and appendix | 81 CT / 146 LOVISA tests; actual fixture/pretrained/legacy transfers and hosted checks |
| LOVISA documentation alignment | Two-project explanation, reused illustrations and concise linked guides | Complete: 81 CT / 146 LOVISA tests, 25 Markdown files per repo and published updates; all hosted checks passed |

The existing detector, package layout and exchange names stay stable in the
LOVISA documentation pass. No patient-data validation, model retraining or new
GPU/NPU execution is claimed complete.

## Public research exchange

Research extension: bounded, source-mapped CT excerpts may be linked to explicitly
fictional composite cases with dataset/license/subject provenance. Existing
synthetic-v2 remains strict. A protocol-unverified research path records uncertainty
instead of asserting that missing contrast information proves noncontrast. Real
CT inference is a research smoke; full RetinaNet training still requires CUDA.

Status: implemented and tested locally — 83 CT tests and actual 11.98-second real-image excerpt inference; full-scan attempt stopped and full CUDA training not executed. Hosted checks passed: https://github.com/LilyC2024/ai-medimg-2.5D-CT/actions/runs/40014638635. Compatible LOVISA receiver is published; final receiver checks follow.

## Systematic three-project review — 24 October 2026

1. **Review/repair:** expert source audit, reproduced defects, focused regressions
   and full suite before documentation changes. Status: passed — 101 runtime
   tests in 34.96s, 22 targeted review/documentation checks and repository Ruff.
2. **Documentation:** concise root README, detailed linked workflows/contracts/
   training/security/function guides and current LOVISA integration. Status: passed —
   31 documents/anchors and generated API references checked; specialist audit
   corrected fresh-install paths, historical slice counts and checker scope.
3. **Joint release:** actual local inference/producer-consumer checks, evidence,
   unchanged or explicitly synchronized contracts and tested publication. Status: complete — 105 local tests, actual registered CPU inference and all
   receiver transfers passed. Source published as 9a3cdfe; hosted 40099064726
   passed Linux/Windows, container and pretrained checks. No new GPU/NPU claim.

## Claude branch integration — 24 October 2026

1. **Branch and runtime review:** inspect every origin branch against `a85538e`,
   integrate compatible signing APIs with shared bounded signature verification,
   and test runtime/security changes before documentation. Status: passed — focused signature/adversarial regressions and full local suite.
2. **Quality gates and documentation:** execute type/coverage/dependency/SBOM
   checks; retain source-agent review history with clear nonclinical attribution;
   integrate data terms, document branch decisions, regenerate source API docs.
   Status: passed — local type, coverage, dependency and documentation checks.
3. **Joint validation and publication:** full tests, exact shared source sync and
   producer/consumer validation before parent-agent publication. Status: complete — published to main; local/joint checks and hosted release/security workflows passed.
