# Retained code and cleanup decisions

[Current release](lung/release.md) · [Legacy change record](release_notes.md)

| Area | Decision and reason |
| --- | --- |
| lung_nodule package | Active detection, source geometry, review, reports and research tooling |
| Shared DICOM loader | Retained tested HU/physical-geometry implementation |
| 2.5D U-Net/teacher/export/Intel tools | Retained reproducible engineering baseline and tissue-mask compatibility |
| Legacy scripts/report.py | Removed obsolete pseudo-label report generator; current research report is source-bound |
| Legacy scripts/make_index.py | Removed redundant alias; prepare_case.py owns preparation |
| Old day-by-day/interview/status documents | Consolidated into current guides and dated evidence; old versions remain in Git history |
| Patient/model/run artifacts | Kept local and ignored, not distributed or silently deleted |
| Duplicate requirements | requirements.txt forwards to pyproject.toml |
| MONAI dependency | Unused in the old tissue experiment; now required by the active lung extras |
| Tests | Full pytest collection includes legacy unittest classes and active function tests |
| Documentation | Concise overview, subject guides, function reference and clearly labeled historical evidence |

Previously tracked identifiers are not erased by cleanup. Data ownership and any
history remediation need separate review. Technical aliases/hashes are not full
anonymization. Namespace migration is unnecessary for the currently tested package
contracts; stable LOVISA bridge names remain documented. [Data rules](lung/data.md).
