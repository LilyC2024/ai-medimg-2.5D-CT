# Research preparation, GPU training and evaluation

[Overview](../../README.md) · [Data permissions](data.md) · [Hardware](deployment.md)

## Establish the experiment first

This release supplies a pretrained inference path and a guarded upstream training
launcher. It does not claim a newly trained or independently validated nodule
model. Obtain permitted public labels, resolve reader annotations and freeze
patient-separated training/validation/test cohorts before training. Audit overlap
with the pretrained model before using it as a benchmark. Never split neighboring
slices of the same patient between cohorts.

Prepare each supported DICOM research volume as physical HU NIfTI:

```bash
.venv/bin/python -m lung_nodule.research prepare-image --series data/research/case001 --approval data/research/approval.json --output data/research/prepared/case001.nii.gz
```

Preparation uses source geometry and linear resampling to the upstream training
spacing .703125/.703125/1.25mm. It does not normalize HU, invent annotations or
assign a patient/split. Save the printed image hash in the manifest. A generated
phantom is supported for software tests but not clinical training claims.

## Manifest

The manifest schema is in [research.py](../../src/lung_nodule/research.py).
Illustrative one-case entry below must be expanded to all three nonempty cohorts;
the placeholder hash and coordinates must be replaced with actual source values.
Use local aliases, not original identifiers.

```json
{
  "schema_version": "lung-nodule-dataset-v1",
  "public_research_approved": true,
  "approved_by": "Actual research approver",
  "dataset": "Collection/version and annotation protocol",
  "license": "Applicable permission",
  "intensity_units": "HU",
  "cases": [{
    "patient_id": "subject001",
    "study_id": "study001",
    "split": "training",
    "image": "case001.nii.gz",
    "image_sha256": "REPLACE_WITH_ACTUAL_64_CHARACTER_SHA256",
    "annotations_complete": true,
    "nodules": [{"center_lps_mm": [12.0, 18.0, 40.0], "diameter_mm": 6.0}]
  }]
}
```

Truth centers use physical **LPS x/y/z**, not voxel coordinates or RAS. Nodule
diameters come from reference annotations; spherical training boxes do not imply
pathology truth. Empty nodules lists are allowed only for annotated negative
volumes under the stated target protocol. Missing labels are never negatives.
Manifest validation rejects cross-split patient/hash leakage, duplicate studies,
incomplete-label attestations, invalid paths, changed bytes, wrong spacing and
truth centers outside the image. Completeness is attested, not independently proven.

```bash
.venv/bin/python -m lung_nodule.research validate --manifest data/research/manifest.json --dataset-root data/research/prepared
```

## CUDA training

Install matching CUDA torch/torchvision wheels, then `pip install -e ".[training]"`.
The referenced upstream configuration requires substantial GPU memory (its model
card documents at least 16GB for its training setup). An Intel NPU is not a training
replacement. Inspect hardware before starting:

```bash
.venv/bin/python scripts/lung_hardware.py --output artifacts/hardware.json
.venv/bin/python -m lung_nodule.research train --manifest data/research/manifest.json --dataset-root data/research/prepared --model-dir models/luna16 --output artifacts/lung-training-001 --epochs 20
```

The launcher requires actual CUDA; no silent CPU fallback. It verifies the local
downloaded bundle, creates an explicit train/validation datalist and materializes
the upstream config with separate validation data. The test cohort is excluded.
It records manifest/config/model identities and running/completed/failed status.
The upstream trainer uses its own random initialization and augmentation; this
command does **not** silently fine-tune the shipped checkpoint. Training is an
experiment, not model promotion. The upstream save uses validation COCO metrics;
that selection is not an independent test FROC result. Use enough epochs to reach
its configured validation interval; the launcher bounds that interval by the
requested epoch count so even a one-epoch run reaches validation. Inspect the
actual generated config/run record.

For a resulting compatible local research checkpoint, detection supports
`--checkpoint path/to/model.pt` in addition to the registered base bundle. Loading
is tensor-only and strict; provenance identifies the supplied checkpoint. No
clinical endorsement or automatic promotion follows from successful loading.
End-to-end GPU training remains **unexecuted** on the CPU-only development host.

## Detection evaluation

The engineering FROC scorer consumes JSON containing one entry per complete scan:

```json
[
  {"study_id":"s1","annotations_complete":true,
   "truths":[{"center_lps_mm":[0,0,0],"diameter_mm":8}],
   "predictions":[{"center_lps_mm":[0,0,0],"score":0.9}]},
  {"study_id":"s2","annotations_complete":true,"truths":[],"predictions":[]}
]
```

Use geometry.to_lps on each candidate's box center to build prediction centers.
Do not use reviewer-filtered detections to report raw model performance. Include
negative volumes. Ground-truth inclusion rules and source cohort identity must
be retained with the experiment.

```bash
.venv/bin/python -m lung_nodule.research evaluate --input artifacts/evaluation-input.json --output artifacts/froc.json
```

The scorer performs one-to-one center-distance matching within half the reference
diameter and counts duplicate detections as false positives. It reports the best
observed sensitivity not exceeding each requested false-positive rate. It is
**LUNA-style, not the official LUNA scorer**: it lacks excluded/irrelevant findings,
official curve interpolation and bootstrap intervals. Use the
[official evaluation](https://luna16.grand-challenge.org/Evaluation/) for challenge
comparisons. Avoid claiming equivalence between COCO AP and FROC sensitivity.

Before usefulness claims, measure external patient/site performance, lesion-size
and subtype failures, false positives, caliper error and report factual errors.
A clinician reader study should include correction time and missed findings.
No quantitative clinical acceptance threshold has been established here.
