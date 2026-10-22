"""Patient-separated research manifests, local GPU training and transparent FROC.

This is an engineering metric, not the official LUNA16 scorer: no challenge
excluded-nodule categories or bootstrap intervals are inferred from absent data.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Literal

import numpy as np
from pydantic import Field, StrictBool, model_validator
from scipy.optimize import linear_sum_assignment

from lung_nodule.contracts import Digest, Identifier, Record, digest
from lung_nodule.sources import sha256


class NoduleTruth(Record):
    center_lps_mm: tuple[float, float, float]
    diameter_mm: float = Field(gt=0, le=100)


class DatasetCase(Record):
    patient_id: Identifier
    study_id: Identifier
    split: str = Field(pattern=r"^(training|validation|test)$")
    image: str
    image_sha256: Digest
    annotations_complete: StrictBool
    nodules: list[NoduleTruth]


class DatasetManifest(Record):
    schema_version: str = Field(pattern=r"^lung-nodule-dataset-v1$")
    public_research_approved: StrictBool
    approved_by: str = Field(min_length=1)
    dataset: str = Field(min_length=1)
    license: str = Field(min_length=1)
    intensity_units: Literal["HU"]
    cases: list[DatasetCase] = Field(min_length=3, max_length=10000)

    @model_validator(mode="after")
    def group_separation(self):
        if not self.public_research_approved:
            raise ValueError("Explicit public research dataset approval required")
        groups = {}
        studies = set()
        hashes = {}
        for c in self.cases:
            if c.study_id in studies:
                raise ValueError("Duplicate study ID")
            studies.add(c.study_id)
            if c.patient_id in groups and groups[c.patient_id] != c.split:
                raise ValueError("Patient leakage across dataset splits")
            if c.image_sha256 in hashes and hashes[c.image_sha256] != c.split:
                raise ValueError("Identical image bytes leak across splits")
            groups[c.patient_id], hashes[c.image_sha256] = c.split, c.split
            if not c.annotations_complete:
                raise ValueError("Incomplete annotations cannot be treated as whole-volume negatives")
            path = Path(c.image)
            if path.is_absolute() or ".." in path.parts or "\\" in c.image or not c.image.endswith((".nii", ".nii.gz")):
                raise ValueError("Use dataset-relative NIfTI image paths")
        if {c.split for c in self.cases} != {"training", "validation", "test"}:
            raise ValueError("Separate nonempty training, validation and test cohorts required")
        return self


def validate_dataset(manifest_path, dataset_root):
    """Check image hashes, LPS-aware affine, HU scale declaration and model spacing."""
    import nibabel as nib

    manifest = DatasetManifest.model_validate_json(Path(manifest_path).read_bytes())
    root = Path(dataset_root).resolve()
    for case in manifest.cases:
        path = (root / case.image).resolve()
        if not path.is_relative_to(root) or sha256(path) != case.image_sha256:
            raise ValueError("Dataset image identity/path mismatch")
        image = nib.load(path)
        if len(image.shape) != 3 or np.prod(image.shape) > 256 * 1024**2 or not np.isfinite(image.affine).all() or abs(np.linalg.det(image.affine[:3,:3])) < 1e-9:
            raise ValueError("Invalid 3D image affine")
        # Upstream training config expects pre-resampled NIfTI; inference resamples raw DICOM.
        if not np.allclose(nib.affines.voxel_sizes(image.affine), [.703125,.703125,1.25], atol=1e-4):
            raise ValueError("Training NIfTI must be resampled to .703125/.703125/1.25mm")
        for nodule in case.nodules:
            ras = np.array(nodule.center_lps_mm) * [-1,-1,1]
            center = np.linalg.solve(image.affine[:3,:3], ras-image.affine[:3,3])
            if np.any(center < 0) or np.any(center > np.array(image.shape)-1):
                raise ValueError("Truth nodule center falls outside source volume")
    return manifest


def prepare_training_image(series, destination, *, approval=None):
    """Write HU NIfTI at upstream training spacing; no labels or split are invented."""
    import SimpleITK as sitk
    from lung_nodule.sources import load_sources

    hu, geometry, _, identity, kind, _ = load_sources(series, approval=approval)
    destination = Path(destination)
    if destination.exists() or not str(destination).endswith((".nii", ".nii.gz")):
        raise ValueError("Select a new .nii or .nii.gz output")
    image = sitk.GetImageFromArray(hu)
    image.SetSpacing(geometry.spacing_zyx_mm[::-1])
    image.SetOrigin(geometry.origin_lps_mm)
    image.SetDirection(geometry.direction_lps)
    spacing = [.703125,.703125,1.25]
    size = [int(round((n-1)*old/new))+1 for n,old,new in zip(image.GetSize(),image.GetSpacing(),spacing)]
    if np.prod(size) > 256 * 1024**2:
        raise ValueError("Prepared image exceeds 256Mi voxel allocation limit")
    output = sitk.Resample(image, size, sitk.Transform(), sitk.sitkLinear,
                           image.GetOrigin(), spacing, image.GetDirection(), -1000., sitk.sitkFloat32)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sitk.WriteImage(output, str(destination))
    return {"image_sha256":sha256(destination),"source_sha256":identity,"input_kind":kind,
            "spacing_xyz_mm":spacing,"units":"HU; no intensity normalization"}


def launch_training(*, manifest_path, dataset_root, model_dir, output, epochs=1):
    """Run the pinned upstream trainer on CUDA with explicit patient-separated data.

    Downloads never occur here. Test cohort is never passed to the training
    subprocess. This launcher does not claim that pretrained weights were unseen
    on any cohort; the dataset/model overlap audit remains a separate requirement.
    """
    from lung_nodule.detection import select_device, verify_model

    select_device("cuda")  # fail before reading data or creating run artifacts
    registration = verify_model(model_dir)
    manifest = validate_dataset(manifest_path, dataset_root)
    if epochs < 1:
        raise ValueError("Epoch count must be positive")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = {}
    for split in ("training", "validation"):
        records[split] = [{"image": c.image, "box": [[*n.center_lps_mm, n.diameter_mm, n.diameter_mm, n.diameter_mm] for n in c.nodules],
                          "label": [0]*len(c.nodules)} for c in manifest.cases if c.split == split]
    datalist = output / "datalist.json"
    datalist.write_text(json.dumps(records, indent=2))
    # Override the upstream 95/5 within-list split with the declared validation cohort.
    overrides = {"bundle_root": str(Path(model_dir).resolve()), "device": "$torch.device('cuda:0')",
        "dataset_dir": str(Path(dataset_root).resolve()), "data_list_file_path": str(datalist),
        "epochs": epochs, "val_interval": min(5, epochs), "amp": True, "ckpt_dir": str(output / "checkpoints"), "output_dir": str(output / "logs"),
        "train#dataset#data": "$@train_datalist",
        "validate#dataset#data": "$monai.data.load_decathlon_datalist(@data_list_file_path,is_segmentation=True,data_list_key='validation',base_dir=@dataset_dir)"}
    # ConfigParser nested overrides are materialized, not encoded as flat keys.
    config = json.loads((Path(model_dir) / "configs/train.json").read_text())
    config.update({k:v for k,v in overrides.items() if "#" not in k})
    config["train"]["dataset"]["data"] = overrides["train#dataset#data"]
    config["validate"]["dataset"]["data"] = overrides["validate#dataset#data"]
    config_path = output / "train.json"
    config_path.write_text(json.dumps(config, indent=2))
    command = [sys.executable, "-m", "monai.bundle", "run", "--config_file", str(config_path)]
    run = {"schema": "lung-nodule-training-run-v1", "status": "running", "device_requested": "cuda:0",
           "dataset_manifest_sha256": sha256(manifest_path), "model_registration": registration,
           "training_config_sha256": sha256(config_path), "test_cohort_used": False,
           "initialization": "upstream training initialization; not automatic fine-tuning", "epochs": epochs}
    record = output / "run.json"
    record.write_text(json.dumps(run, indent=2))
    try:
        subprocess.run(command, cwd=Path(model_dir).resolve(), check=True)
    except BaseException:
        run["status"] = "failed-or-interrupted"
        record.write_text(json.dumps(run, indent=2))
        raise
    run["status"] = "completed-unvalidated-research-training"
    record.write_text(json.dumps(run, indent=2))
    return output


def froc(cases, operating_points=(.125, .25, .5, 1., 2., 4., 8.)):
    """Center-distance matching on complete volumes; duplicates count as false positives.

    Input per scan: truths[{center_lps_mm,diameter_mm}], predictions[{center_lps_mm,score}].
    Include genuinely negative scans in the denominator. No bootstrapped CI is claimed.
    """
    if not cases or len({c["study_id"] for c in cases}) != len(cases):
        raise ValueError("Nonempty, unique complete-volume studies required")
    total = sum(len(c["truths"]) for c in cases)
    if not total:
        raise ValueError("Sensitivity is undefined without positive truth nodules")
    thresholds = {float("inf")}
    for c in cases:
        if c.get("annotations_complete") is not True:
            raise ValueError("Complete annotation attestation required")
        for truth in c["truths"]:
            NoduleTruth.model_validate(truth)
        for pred in c["predictions"]:
            if len(pred["center_lps_mm"]) != 3 or not np.isfinite([*pred["center_lps_mm"], pred["score"]]).all() or not 0 <= pred["score"] <= 1:
                raise ValueError("Invalid prediction center/score")
            thresholds.add(float(pred["score"]))
    curve = []
    for threshold in sorted(thresholds, reverse=True):
        hits = false = 0
        for case in cases:
            preds = [p for p in case["predictions"] if p["score"] >= threshold]
            truths = case["truths"]
            matched = 0
            if preds and truths:
                distances = np.linalg.norm(np.array([p["center_lps_mm"] for p in preds])[:,None,:] - np.array([t["center_lps_mm"] for t in truths])[None,:,:], axis=2)
                edges = distances <= np.array([t["diameter_mm"]/2 for t in truths])
                rows, cols = linear_sum_assignment(-edges.astype(int))
                matched = int(edges[rows,cols].sum())
            hits += matched
            false += len(preds)-matched
        curve.append({"threshold": None if np.isinf(threshold) else threshold,
                      "sensitivity": hits/total, "false_positives_per_scan": false/len(cases)})
    sensitivities = [max(p["sensitivity"] for p in curve if p["false_positives_per_scan"] <= fp) for fp in operating_points]
    return {"schema": "research-center-froc-v1", "scans": len(cases), "truth_nodules": total,
            "operating_points_fp_per_scan": list(operating_points), "sensitivities": sensitivities,
            "mean_sensitivity": float(np.mean(sensitivities)), "curve": curve,
            "limitations": "Engineering center-distance FROC; not official LUNA scoring. No irrelevant-finding exclusions or bootstrap CIs. Cohort completeness is attested, not proven."}


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for command in ("validate", "train"):
        q = sub.add_parser(command)
        q.add_argument("--manifest", required=True)
        q.add_argument("--dataset-root", required=True)
        if command == "train":
            q.add_argument("--model-dir", required=True)
            q.add_argument("--output", required=True)
            q.add_argument("--epochs", type=int, default=1)
    q = sub.add_parser("evaluate")
    q.add_argument("--input", required=True)
    q.add_argument("--output", required=True)
    q = sub.add_parser("prepare-image")
    q.add_argument("--series", required=True)
    q.add_argument("--output", required=True)
    q.add_argument("--approval")
    a = p.parse_args(argv)
    if a.command == "validate":
        manifest = validate_dataset(a.manifest, a.dataset_root)
        print(json.dumps({"cases":len(manifest.cases),"manifest_digest":digest(manifest)}))
    elif a.command == "train":
        print(launch_training(manifest_path=a.manifest,dataset_root=a.dataset_root,model_dir=a.model_dir,output=a.output,epochs=a.epochs))
    elif a.command == "prepare-image":
        print(json.dumps(prepare_training_image(a.series,a.output,approval=a.approval)))
    else:
        result = froc(json.loads(Path(a.input).read_text()))
        Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False))
        print(json.dumps(result))


if __name__ == "__main__":
    main()
