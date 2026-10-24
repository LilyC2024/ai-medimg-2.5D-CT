# Intended use and clinical boundary

[Overview](../README.md) · [Model card](lung/model-card.md) · [LOVISA integration](lung/mhcra.md)

The CT application is a local educational/research assistant for source-image
inspection, candidate annotations and reviewable measurements. LOVISA organizes
fictional histories and prepares a source-linked report for human review. Neither
is supplied as a diagnostic, treatment, triage or automatic medical-decision system.
No certification, regulatory clearance, cancer-diagnosis performance or clinical
reader-time benefit is claimed.

Calling an application research does not establish that a future clinical use is
permitted. A clinical extension would need a separately defined intended purpose,
qualified oversight, permitted representative data, risk/security/usability work
and independent clinical/regulatory assessment. Current synthetic tests and
historical NPU timing provide none of that clinical authorization.

The former head-CT/hemorrhage research idea was exploratory and is not the current
lung deliverable. Current development targets lung-nodule **candidates**, not all
abnormalities, malignancy classification or management recommendations. Do not
infer an unimplemented indication from an old project note.

The current code review strengthens input/evidence checks and error handling; it
adds no clinical indication, regulatory certification or automatic decision.
Public research images in LOVISA remain linked only to explicitly fictional
composite cases with unrelated subject provenance. [Security](../SECURITY.md) ·
[Current expert review](review.md).
