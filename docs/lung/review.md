# Review, measurements and reporting

[Overview](../../README.md) · [Contracts](code-reference.md)

1. Generate a fixture or run pretrained detection. Outputs remain unreviewed.
2. Start the loopback UI and enter the workspace directory, not its parent.
3. Jump to each candidate; inspect source and amber-box overlay across relevant
   slices. Indices are zero-based; the visible source slice hash identifies evidence.
   The display does not infer patient left/right markers.
4. Accept/reject every candidate. Uncertain blocks completion. Acceptance means a
   research candidate is retained; it does not diagnose malignancy.
5. Optionally enable a caliper and enter source slice plus start/end row/column.
   **Preview measurements** draws a cyan line and calculated length. Forms commit
   widgets together: enabling a caliper may need a preview submission before the
   coordinate inputs appear. Endpoints must lie within the candidate box.
6. Enter the actual reviewer identifier and explicitly attest qualification and
   image/measurement review. **Complete research review** persists approval only
   after validation. Tests use scripted synthetic attestations, not real clinicians.
7. Saved calipers and a report appear after success. Every download rechecks source
   integrity and reconstructs text; editing report.md does not alter observations.

The standalone UI has no login/credential registry and must remain local. This
research attestation is not MHCRA's authenticated final clinical approval.

## Measurement semantics

Detector AABB extents are physical source-grid box spans, not lesion diameters,
segmentation volumes or RECIST. Manual calipers are geometry-aware Euclidean
source-plane distances. Their appropriateness remains a human judgment. No manual
contouring or box-editing tool exists; reject an unsuitable candidate box.

## Workspace

| File | Purpose |
| --- | --- |
| study.json | Candidates, sources, geometry and model provenance |
| source.npy | Float32 source-grid HU snapshot; not original DICOM |
| integrity.json | Snapshot and pixel-file digests |
| review.json | Decisions, calipers and content-bound local attestation |
| report.md | Convenience text, regenerated from verified structured data |

Original DICOM is never modified. Keep it for independent evidence reconstruction.
Workspaces belong under ignored artifacts/. Acquisition date/prior comparison are
unavailable and stated explicitly; file timestamps are never substituted.

## CLI

An expert may author Review JSON using the [schema](../../src/lung_nodule/contracts.py),
including exact `digest(study)`, every decision, reviewer and literal true approval
and qualification fields. No auto-approve option exists.

```bash
.venv/bin/python -m lung_nodule.cli review --workspace artifacts/pretrained-demo --approval path/to/actual-review.json
.venv/bin/python -m lung_nodule.cli export --workspace artifacts/pretrained-demo --output artifacts/nodules.zip
```

Export requires valid review and generated-synthetic input. The new exchange
format is not directly accepted by MHCRA's old importer. [Integration](mhcra.md).


Current v2 exports include bounded source HU and every-slice previews for the
implemented MHCRA viewer/calipers. The default standalone export still requires
your explicit CT review. MHCRA repeats authenticated imaging review and final
clinical approval; upstream attestation never bypasses those gates. [Integration](mhcra.md).
