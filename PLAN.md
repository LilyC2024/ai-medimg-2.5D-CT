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
   compilation and Markdown link checks. Initial release published; its real
   pretrained CI smoke passed. Windows found a default-codec failure; explicit
   UTF-8 IO and portability regressions passed locally. Repaired hosted CI pending.
