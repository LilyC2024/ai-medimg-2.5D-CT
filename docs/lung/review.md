# Review CT candidates and measurements

[Overview](../../README.md) · [LOVISA transfer](mhcra.md) · [Contracts](code-reference.md)

## Standalone review

1. Generate a fixture or run installed pretrained detection. Open its **workspace**
   in the loopback Streamlit UI. Outputs start unreviewed.
2. Jump to each candidate and inspect source slices plus amber boxes. Indices are
   zero-based; the displayed source hash identifies evidence. No left/right or lobe
   label is inferred.
3. Accept or reject every candidate. “Uncertain” blocks completed review. Acceptance
   retains a research candidate; it does not establish malignancy.
4. Optionally enable an in-plane caliper and supply source slice, start/end row and
   column. **Preview measurements** draws cyan and shows physical length. Form
   inputs appear after a preview submission when the caliper is first enabled.
5. Enter the actual reviewer identifier, attest qualification and image/measurement
   review, then **Complete research review**. Validation precedes approval persistence.
6. Download the summary. Each download rechecks source integrity and regenerates
   text; editing report.md cannot change structured findings or approve a report.

The UI has no login/credential registry. Its local attestation is distinct from
LOVISA's authenticated imaging acceptance and final clinical approval. Tests use
scripted reviewers, not clinician validation. Keep it local.

## What the numbers mean

Box extents are source-grid AABB spans, not lesion diameters, volume or RECIST.
Calipers are geometry-aware Euclidean distances on one integer source plane;
endpoints must lie inside the accepted candidate box. Human judgment determines
whether placement is appropriate. There is no contour/box-editing tool: reject an
unsuitable candidate. No accepted candidates does not establish normality.

## Workspace files

| File | Purpose |
| --- | --- |
| study.json | Candidates, geometry, ordered sources and model provenance |
| source.npy | Float32 source HU snapshot; not original DICOM |
| integrity.json | Study and source-array digests |
| review.json | Explicit decisions/calipers and content-bound local attestation |
| report.md | Convenience text reconstructed from validated structured data |

Original DICOM stays unchanged; retain it for independent reconstruction. Use ignored
`artifacts/` and new output directories. Dates/prior comparison are unavailable;
file timestamps are not substituted.

## CLI and LOVISA export

A reviewer may author Review JSON against [contracts.py](../../src/lung_nodule/contracts.py),
with exact study digest, every decision and explicit qualification/approval fields:

```bash
.venv/bin/python -m lung_nodule.cli review --workspace artifacts/pretrained-demo --approval path/to/actual-review.json
.venv/bin/python -m lung_nodule.cli export --workspace artifacts/pretrained-demo --output artifacts/nodules.zip
```

Default export requires completed CT review and generated-synthetic input. Current
nodule-v2 includes bounded HU and every-slice previews and is accepted by LOVISA's
nodule importer. The dedicated bridge can instead create **pending** input for
LOVISA review; it does not forge a CT approval. Both paths require LOVISA's own
imaging acceptance and separate final report approval. [Exact workflow](mhcra.md).

## Retry and integrity boundaries

Source snapshots must be finite real float32-representable data matching geometry.
Bad input is rejected before output reservation. A completed review never repairs
an inconsistent source or source mapping. Original DICOM remains separate; hashes
prove internal identity, not actual anonymization, producer execution or clinical
truth. Public research excerpts use a separate provenance-bound export path and
still require LOVISA image acceptance. [Public demo](public-demo.md).
