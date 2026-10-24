# CT architecture and coordinate contracts

[Overview](../../README.md) · [Functions](code-reference.md) · [LOVISA connection](mhcra.md)

## Processing sequence

1. **Load and identify:** `sources.load_sources` checks approval/input kind,
   validates one regular series and retains ordered HU, geometry, source-byte
   hashes and hashed SOP identities. Mixed identity/geometry or changed bytes fail.
2. **Verify the detector:** `MonaiDetector` verifies local registration/config/
   weight hashes and strictly loads tensor-only weights. Inference does not
   evaluate downloaded configuration expressions or fetch missing assets.
3. **Prepare:** source z/y/x HU becomes channel/x/y/z MetaTensor, LPS affine becomes
   RAS, spacing becomes .703125/.703125/1.25 mm, and HU [−1024,300] maps to [0,1].
4. **Detect/map:** 3D RetinaNet proposes boxes; all eight corners transform through
   resampled affine, RAS→LPS and inverse source geometry. Source AABBs are clipped
   to valid voxel centers; degenerate/outside boxes are discarded.
5. **Persist/review:** a new workspace stores Study, float32 source HU and digests.
   Source/candidate/caliper inspection requires explicit decisions. Uncertainty
   blocks completion. Downloads revalidate and reconstruct deterministic report text.

## Model

The MONAI reference topology uses 3D ResNet50, FPN layers [1,2], three anchor shapes
and one nodule class. NMS IoU is .22; default score threshold .15 is an engineering
setting, not a clinically validated operating point. The fixed upstream revision
and adapted recipe are recorded in registration/provenance.

Inference uses 192×192×80 sliding windows to bound working memory, rather than the
upstream 512×512×192 ROI. That adaptation needs its own full-volume accuracy
assessment; upstream metrics cannot be inherited. [Model card](model-card.md).

## Coordinates and measurements

| Representation | Convention |
| --- | --- |
| Arrays / box coordinates | Source z/y/x voxel centers |
| Physical positions | LPS x/y/z, including origin, spacing and full direction matrix |
| Network representation | RAS-resampled MetaTensor |
| Box extents | Source AABB spans; not lesion diameters, segmentation volume or RECIST |
| Calipers | Nonzero Euclidean distance on one integer source plane, endpoints inside the candidate box |

An oblique AABB can enlarge the mapped network box. Candidate IDs belong to one
study; they are not longitudinal lesion identities. No laterality/lobe, prior
comparison or acquisition date is inferred.

## Runtime and trust

CT has no LLM agents. Python performs source/geometry/review/report operations;
RetinaNet is the CV detector. The separate non-ML fixture finder is synthetic-only.
Reviewer identifiers are local attestations, not authenticated credentials.
Keep Streamlit on loopback. Hashes establish consistency, not independent origin,
anonymization, model-execution authenticity or clinical truth.

LOVISA receives bounded synthetic nodule-v2 or separately labelled public
research-v3 excerpts and performs independent validation, authenticated imaging
acceptance and final clinical approval. Its
images/notes stay outside local Ollama. [Integration contract](mhcra.md).

## Numeric and persistence preflight

Workspace creation validates source shape, finite real numeric values and float32
representability before reserving a directory. Training preflight checks actual
finite real voxel data as well as hashes/affine/spacing. Invalid target labels are
rejected before integer conversion in the retained 2.5D dataset path. These checks
prevent a successful-looking artifact from hiding corrupted input.

![Relationship to history, endoscopy and human review](../images/lovisa-system.svg)

The sketch describes component responsibilities, not accuracy or patient linkage.
[Expert repairs](../review.md) · [Function inventory](code-reference.md).
