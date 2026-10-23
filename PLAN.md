# Lung nodule research assistant implementation

Complete and test each phase before starting the next. No clinical accuracy or
accelerator execution is inferred from synthetic fixtures or historical results.

1. Foundation: preserve legacy compatibility; add versioned source geometry,
   candidate, review and measurement contracts; generated chest phantom; test
   coordinate transforms, evidence binding and invalid input. Passed: baseline 32
   tests; 6 new foundation tests. Torch 2.14.1+cpu, MONAI 1.6.1 inspected.
2. Detection: local MONAI RetinaNet adapter, explicit CPU/CUDA selection, offline
   checkpoint registration, full-volume inference and synthetic smoke. Test real
   network construction separately from scripted detector tests. Passed: 10
   foundation/detection tests; official 80MB checkpoint loaded strictly and ran on
   generated 32x64x64 phantom (1 candidate, 5.78s CPU including load). Fixed a
   mismatched torchvision wheel by installing the matching CPU wheel. No patient
   detection evaluation or accelerator run is claimed.
3. Review: local UI, source/annotation inspection, candidate decisions, calipers,
   content-bound approval, deterministic evidence-linked report and portable
   synthetic exchange. Passed: 20 cumulative nodule tests, including Streamlit
   AppTest, rejected/stale approvals and source/report tampering. Calipers are
   source-plane measurements, box extents are explicitly not lesion diameters.
4. Research/deployment: patient-separated dataset manifest validation, LUNA-style
   FROC evaluation, explicit GPU training launcher and hardware diagnostics.
   Preserve historical CPU/Intel NPU tools without transferring their claims.
   Test validation and unavailable-device failure paths. Passed: 29 cumulative
   tests before documentation, with dataset hash/spacing validation, patient and
   byte leakage rejection, negative-scan/duplicate FROC behavior and explicit
   unavailable-CUDA failure. Hardware inspection: this host has no CUDA/OpenVINO.
   Actual GPU training/NPU inference and clinical cohort evaluation are unexecuted.
5. Documentation/release: concise root overview and detailed module/folder guides,
   architecture figure, actual evaluation record, both compatibility suites,
   public-content review and GitHub publication. Local gates passed: 68 CT tests,
   120 unchanged MHCRA tests, actual pretrained CPU smoke, random-weight tiled
   forward, real upstream trainer construction (not training), lint, dependency,
   compilation and Markdown link checks. Published implementation 5bb2c9b passed
   repaired hosted Windows/Linux suites, actual pretrained phantom smoke and
   Linux Docker new/legacy checks. The initial Windows default-codec failure was
   fixed with explicit UTF-8 IO and portability regressions. Complete; clinical
   accuracy, GPU training and new-detector NPU execution remain explicitly outside
   the demonstrated results, not silently marked passed.

## Coordinated MHCRA compatibility — v0.10.0

- Producer phase: shared ML-free schema/report/rendering, bounded every-slice/HU
  nodule-v2 export and pending-review bridge. Passed 26 producer/review tests.
- Consumer phase in MHCRA: typed candidate/caliper decisions, authenticated
  acceptance, source-linked report appendix; legacy contract retained. Passed
  companion regression before joint smoke.
- Joint phase: actual local fixture, installed-pretrained CPU and legacy
  producer/consumer smokes passed with no approvals issued. Both suites, shared
  contract drift, documentation links and hosted CI tracked in EVALUATION.md.

Hosted joint phase passed: CT Windows/Linux, Docker and pretrained jobs; MHCRA
Python 3.10/3.12 plus fixture/pretrained/legacy integration. Both implementations
published; exact commits and run links are recorded in EVALUATION.md.
