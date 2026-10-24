# CT inputs, permissions and source evidence

[Overview](../../README.md) · [Training](training.md) · [LOVISA integration](mhcra.md)

## Supported volume

One directory must contain one regular single-frame monochrome CT series.
The lung path allows at most **512 slices**, **1024 pixels per plane dimension**
and **128 Mi source voxels**; resampling has a separate **256 Mi voxel** limit.
The legacy loader default is 64 Mi voxels. Oversized volumes fail before allocation;
none are silently truncated.

Required geometry/identity checks reject localizers, multiframe CT, mixed dimensions,
mixed studies/frames, duplicate SOP identities, irregular positions and gantry
shift. Regular oblique geometry is supported; at least two slices are required.
Public research input requires ≤2.5 mm slice spacing and ≤1.5 mm in-plane spacing.

Intended research protocol is complete adult noncontrast chest CT. Coverage and
protocol are operator attestations, not automatic image classifications. A JPEG
or single screenshot does not provide the required volume geometry. Clinical
upload/diagnostic use is unsupported. [Scope](../regulatory_scope.md).

## Generated fixture

The equation-generated phantom has 32×64×64 pixels, 1.5×1×1 mm spacing and an
optional known 8 mm sphere. No patient pixels/headers are copied. The non-ML
component finder uses score 1 as a fixture sentinel and rejects public input.
A neighboring source-hash marker detects changed bytes, but is not independent
proof of origin because a trusted local operator can rewrite it.

## Public research approval

Obtain permitted deidentified research data separately and keep it outside Git and
LOVISA's fictional database. Nothing downloads a patient dataset automatically.
Supply an approval file with the real dataset/version, terms and approving operator:

```json
{
  "public_research_only": true,
  "dataset": "Permitted collection and version",
  "license": "Applicable terms and access permission",
  "approved_by": "Actual approving research operator",
  "protocol": "adult-noncontrast-chest-complete"
}
```

Pass it using `--approval` to detection/preparation. This attests permission/scope;
it does not independently prove anonymization or ethics approval. Never relabel
public/clinical data as synthetic. LOVISA accepts public research only through the separate research-v3 schema and a labelled fictional composite case; synthetic-v2 still rejects public input.

## Dataset and licensing boundaries

LUNA16 location/fold evaluation, LIDC-IDRI reader annotations and later malignancy
research answer different questions. Reader malignancy ratings are not uniformly
pathology truth. The pretrained model uses LUNA16 development data: audit overlap
before any independent evaluation. Split by patient, include genuinely annotated
negatives and never interpret missing labels as negative truth.

No independent multi-patient clinical cohort has been evaluated. One permitted
LIDC-IDRI subject was used for the separately declared annotation-selected ROI
localization smoke; it is not a clinical benchmark.
[Training/evaluation protocol](training.md) separates implemented tooling from
unexecuted experiments. Code is MIT; model assets/upstream code/datasets retain
separate terms. `fetch-model` retains upstream licenses. Commit no patient images,
original identifiers, weights, local approvals or reviewer workspaces.

Public data with unconfirmed acquisition protocol may use the explicit `public-chest-protocol-unverified` research path; this is not noncontrast confirmation or clinical validation. A declared contrast agent conflicts with the older noncontrast attestation and is rejected.

## Revalidation guarantees

Training NIfTI must have finite real numeric source voxels, expected spacing and
valid affine; a valid file hash alone is insufficient. The legacy segmentation
loader checks finite real integer labels in range before conversion, so fractional
values cannot silently become classes. These checks preserve input meaning rather
than repairing or guessing invalid data. [Review findings](../review.md).
