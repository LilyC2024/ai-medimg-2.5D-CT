# Input, research data and licensing

[Overview](../../README.md) · [Training](training.md)

## Supported input

One directory containing only one regular single-frame monochrome DICOM CT series.
Lung-path limits: 512 slices, 1024 pixels per in-plane dimension, 128Mi source
voxels. The legacy loader default remains 64Mi. Resampling has a separate 256Mi
voxel allocation limit and fails before an oversized output allocation.
Reject localizers, multiframe images, mixed dimensions/series, duplicate/irregular
positions and in-plane displacement/gantry tilt. Regular oblique geometry works.
The nodule path requires consistent study/frame identities, unique SOP identities
and at least two slices.

Public research input requires <=2.5mm slice spacing and <=1.5mm in-plane pixels.
Intended protocol: complete adult noncontrast chest CT. The operator attests scope;
software does not establish coverage from BodyPartExamined. Unsupported volumes
fail, rather than being truncated. No screenshot or clinical upload service exists.

## Generated data

The chest-like phantom has 32 slices, 64x64 pixels, 1.5x1x1mm spacing and an optional
known 8mm sphere. The deterministic component finder is non-ML, rejects public
research input, and uses score 1 as a fixture sentinel. Changed bytes invalidate
the neighboring hash marker; a trusted operator can nevertheless rewrite markers.

## Public research approval

Obtain permitted deidentified research DICOM separately. Keep data outside Git and
MHCRA's fictional patient database. No dataset downloads automatically. Create:

```json
{
  "public_research_only": true,
  "dataset": "Permitted public collection and version",
  "license": "Applicable terms and access permission",
  "approved_by": "Actual approving research operator",
  "protocol": "adult-noncontrast-chest-complete"
}
```

Pass `--approval path/to/file.json` to detection/preparation. This is an operator
attestation, not proof of anonymization or ethics approval. Never mark real data
synthetic. MHCRA nodule exchange rejects all public research input.

## Dataset strategy

- [LUNA16](https://luna16.grand-challenge.org/Procedure/): volumetric location
  benchmark and official folds; use official scoring for challenge claims.
- [LIDC-IDRI](https://www.cancerimagingarchive.net/collection/lidc-idri/): original
  DICOM and reader XML. Resolve reader disagreements explicitly. Subjective
  malignancy ratings are not uniformly pathology-confirmed diagnoses.
- [LUNA25](https://luna25.grand-challenge.org/overview-goals/): later malignancy-risk
  research, not a substitute for whole-scan detection evaluation.

No real public dataset was imported/evaluated in this release. Audit overlap with
the pretrained model's LUNA16 development data before claiming independent results.
Split by patient, include genuine negatives, and never treat missing annotation as
negative truth. LUNA irrelevant/excluded findings need official scorer handling.

## Licenses and privacy

Original code is MIT; upstream MONAI code/weights and datasets have separate
licenses/notices. `fetch-model` retains official LICENSE and data-license files.
Do not commit weights, patient images, original identifiers, research approvals,
local reviewer names or workspaces. Public reports in this repository contain
synthetic/technical results only. Dataset permission is separate from code licensing.
