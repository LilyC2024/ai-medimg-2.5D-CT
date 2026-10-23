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

Status: implemented and tested locally — 83 CT tests and actual 11.98-second real-image excerpt inference; full-scan attempt stopped and full CUDA training not executed. Compatible LOVISA publishing and hosted checks follow.
