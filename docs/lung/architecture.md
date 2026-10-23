# Architecture and trust boundaries

[Overview](../../README.md) · [Function reference](code-reference.md)

## Processing flow

1. `sources.load_sources`: approve input kind; hash original DICOM; load ordered HU
   through the shared loader; reject mixed studies/frame identities and changed
   bytes; retain slice hashes and hashed SOP identities.
2. `MonaiDetector`: verify local downloaded artifacts; construct the pinned network;
   load tensor-only weights strictly. Downloaded configuration is not evaluated
   during inference.
3. `prepare_tensor`: source z/y/x HU becomes channel/x/y/z MetaTensor. LPS affine
   becomes RAS, orientation becomes RAS, spacing becomes .703125/.703125/1.25mm,
   and HU [-1024,300] maps to [0,1]. There is no head-region crop.
4. All eight predicted box corners transform through resampled affine, RAS→LPS and
   inverse source geometry. Source-grid AABBs clip to valid voxel centers;
   degenerate/outside boxes are discarded.
5. `workspace` persists a new study and float32 HU snapshot plus digests. Every
   review/report revalidates study, array hash and bounded NPY header.
6. UI supports source/overlay inspection, candidate decisions and manual in-plane
   calipers. All candidates need accept/reject; uncertainty blocks completion.
7. Report text is recomposed from validated study/review on every download. Editing
   report.md cannot confer approval or change exported observations.

## Model and geometry

MONAI reference topology: 3D ResNet50, FPN returned layers [1,2], three anchor
shapes, one nodule class, RetinaNet heads. NMS IoU .22; default configurable score
threshold .15 is an engineering default, not a clinically validated operating
point. Candidate IDs belong to one study, not longitudinal lesion identities.

Topology follows the [Apache-2.0 MONAI bundle](https://github.com/Project-MONAI/model-zoo/tree/dev/models/lung_nodule_ct_detection).
Download revision and file hashes are saved in registration.json. Model/recipe
hashes accompany every study. Large-volume inference uses 192x192x80 sliding
windows to limit working memory, rather than the upstream 512x512x192 inference
ROI. This adaptation is recorded in the recipe digest and needs its own accuracy
evaluation; it is not assumed numerically equivalent on full-size studies.

Arrays use z/y/x, physical positions use LPS x/y/z. `Geometry.to_lps/from_lps` use
the complete direction, origin and spacing. Box extents are center-to-center AABB
spans, not lesion diameters, volumes or RECIST. An oblique source AABB may enlarge
the transformed model box. Calipers require one integer source plane, nonzero
length and endpoints inside the reviewed candidate box.

## Trust boundaries

Hashes establish consistency, not independent authenticity or medical truth. A
trusted local operator can re-author code/manifests. Reviewer names are local
attestations, not authenticated credentials. Bind Streamlit to loopback only.
Protocol/coverage are operator attestations; geometry checks do not establish
clinical scope or anonymization. Dates remain unavailable. No prior comparison,
lobar classification, malignancy classifier or management recommendation exists.
No LLM or inference API is called. [MHCRA](mhcra.md) retains separate authenticated
clinical gates. Its current nodule-v2 importer validates source HU, annotations and
reviewable calipers separately from the retained legacy tissue-mask v1 path.
