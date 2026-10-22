import json

import pytest
from pydantic import ValidationError

from lung_nodule.research import (
    DatasetManifest,
    froc,
    launch_training,
    prepare_training_image,
    validate_dataset,
)
from lung_nodule.phantom import generate_chest


def manifest():
    return {
        "schema_version": "lung-nodule-dataset-v1",
        "public_research_approved": True,
        "approved_by": "test-only",
        "dataset": "synthetic test",
        "license": "synthetic fixture",
        "intensity_units": "HU",
        "cases": [
            {
                "patient_id": f"p{i}",
                "study_id": f"s{i}",
                "split": split,
                "image": f"case{i}.nii.gz",
                "image_sha256": str(i) * 64,
                "annotations_complete": True,
                "nodules": [],
            }
            for i, split in enumerate(("training", "validation", "test"))
        ],
    }


@pytest.mark.parametrize(
    "issue", ["patient", "duplicate", "hash", "incomplete", "approval", "path"]
)
def test_research_manifest_rejects_leakage_and_unknown_negatives(issue):
    data = manifest()
    if issue == "patient":
        data["cases"][1]["patient_id"] = "p0"
    if issue == "duplicate":
        data["cases"][1]["study_id"] = "s0"
    if issue == "hash":
        data["cases"][1]["image_sha256"] = "0" * 64
    if issue == "incomplete":
        data["cases"][0]["annotations_complete"] = False
    if issue == "approval":
        data["public_research_approved"] = False
    if issue == "path":
        data["cases"][0]["image"] = "../escape.nii.gz"
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(data)


def test_froc_counts_duplicates_negatives_and_one_to_one_matches():
    cases = [
        {
            "study_id": "positive",
            "annotations_complete": True,
            "truths": [{"center_lps_mm": [0, 0, 0], "diameter_mm": 8}],
            "predictions": [
                {"center_lps_mm": [0, 0, 0], "score": 0.9},
                {"center_lps_mm": [1, 0, 0], "score": 0.8},
            ],
        },
        {
            "study_id": "negative",
            "annotations_complete": True,
            "truths": [],
            "predictions": [{"center_lps_mm": [2, 0, 0], "score": 0.8}],
        },
    ]
    result = froc(cases)
    assert result["scans"] == 2 and result["mean_sensitivity"] == 1.0
    assert result["curve"][-1]["false_positives_per_scan"] == 1.0
    cases[1]["annotations_complete"] = False
    with pytest.raises(ValueError):
        froc(cases)


def test_training_requires_actual_cuda_before_creating_output(tmp_path, monkeypatch):
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(ValueError, match="unavailable"):
        launch_training(
            manifest_path="absent",
            dataset_root="absent",
            model_dir="absent",
            output=tmp_path / "out",
        )
    assert not (tmp_path / "out").exists()


def test_prepare_hu_nifti_and_manifest_hash_validation(tmp_path):
    pytest.importorskip("nibabel")
    data = manifest()
    for i, case in enumerate(data["cases"]):
        series = generate_chest(tmp_path / f"ct{i}", seed=i)
        result = prepare_training_image(series, tmp_path / case["image"])
        case["image_sha256"] = result["image_sha256"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data))
    assert len(validate_dataset(path, tmp_path).cases) == 3
    (tmp_path / data["cases"][0]["image"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="identity"):
        validate_dataset(path, tmp_path)


def test_training_launcher_excludes_test_cohort_and_overrides_upstream_split(
    tmp_path, monkeypatch
):
    import lung_nodule.detection as detection
    import lung_nodule.research as research

    model = tmp_path / "model"
    (model / "configs").mkdir(parents=True)
    (model / "configs/train.json").write_text(
        json.dumps(
            {
                "train": {"dataset": {"data": "old"}},
                "validate": {"dataset": {"data": "old"}},
            }
        )
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest()))
    monkeypatch.setattr(detection, "select_device", lambda _: "cuda:0")
    monkeypatch.setattr(
        detection, "verify_model", lambda _: {"test": "scripted registration"}
    )
    monkeypatch.setattr(
        research,
        "validate_dataset",
        lambda *_: DatasetManifest.model_validate(manifest()),
    )
    calls = []
    monkeypatch.setattr(
        research.subprocess, "run", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    out = launch_training(
        manifest_path=manifest_path,
        dataset_root=tmp_path,
        model_dir=model,
        output=tmp_path / "run",
    )
    data = json.loads((out / "datalist.json").read_text())
    assert set(data) == {"training", "validation"} and "case2" not in json.dumps(data)
    config = json.loads((out / "train.json").read_text())
    assert config["train"]["dataset"]["data"] == "$@train_datalist"
    assert "validation" in config["validate"]["dataset"]["data"]
    assert calls and calls[0][1]["check"] is True
