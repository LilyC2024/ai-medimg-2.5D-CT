"""Regressions from the three-project expert review; inference is scripted here."""

import hashlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import zipfile

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from data.ct25d_dataset import CT25DDataset
from lung_nodule.detection import PhantomDetector, detect_study
from lung_nodule.phantom import generate_chest
from lung_nodule.research import validate_dataset
from lung_nodule.workspace import load_workspace, save_workspace
from deploy.inference_runtime import unzip_series_bytes


def test_duplicate_source_members_fail_before_extraction():
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("series/slice.dcm", b"first source")
        archive.writestr("series/./slice.dcm", b"replacement source")
    with pytest.raises(ValueError, match="Duplicate archive member"):
        unzip_series_bytes(payload.getvalue())


def test_encrypted_archive_returns_supported_input_error():
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("slice.dcm", b"scripted source")
    raw = bytearray(payload.getvalue())
    # Set the ZIP general-purpose encryption flag in real central/local headers.
    raw[6:8] = (1).to_bytes(2, "little")
    central = raw.index(b"PK\x01\x02")
    raw[central + 8 : central + 10] = (1).to_bytes(2, "little")
    with pytest.raises(ValueError, match="Encrypted archives"):
        unzip_series_bytes(bytes(raw))


@pytest.mark.parametrize(
    "folder", ["series", "ct25d_dicom_user", "outer/ct25d_dicom_user"]
)
def test_api_cleans_owned_root_regardless_of_uploaded_directory_name(
    tmp_path, monkeypatch, folder
):
    import deploy.app as api

    calls = []

    def scripted_runtime(**kwargs):
        # Exercise real archive extraction and cleanup, not clinical inference.
        series = Path(kwargs["series_dir"])
        assert (series / "slice.dcm").read_bytes() == b"scripted archive fixture"
        calls.append(series)
        output = Path(kwargs["output_dir"])
        mask, technical = output / "mask.npz", output / "technical.json"
        mask.write_bytes(b"scripted mask")
        technical.write_text("{}", encoding="utf-8")
        return SimpleNamespace(
            output_paths=SimpleNamespace(
                mask_volume_path=mask,
                preprocess_report_path=technical,
            )
        )

    monkeypatch.setattr(api, "run_deployment_inference", scripted_runtime)
    for name, value in {
        "ready": True,
        "checkpoint_path": tmp_path / "scripted.pt",
        "onnx_path": tmp_path / "scripted.onnx",
        "checkpoint": {},
        "session": object(),
    }.items():
        monkeypatch.setattr(api.app.state, name, value, raising=False)
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr(f"{folder}/slice.dcm", b"scripted archive fixture")
    before = set(Path(tempfile.gettempdir()).glob("ct25d_*"))
    client = TestClient(
        api.app
    )  # Scripted ready state; do not run model-loading lifespan.
    result = client.post(
        "/predict", files={"dicom_zip": ("series.zip", payload.getvalue())}
    )
    assert result.status_code == 200
    assert calls and not calls[0].exists()
    assert set(Path(tempfile.gettempdir()).glob("ct25d_*")) == before


@pytest.mark.parametrize("invalid", [1.5, np.nan, np.inf, -1, 4, 1j])
def test_legacy_dataset_rejects_labels_before_integer_cast(tmp_path, invalid):
    np.savez(
        tmp_path / "volume.npz",
        volume=np.zeros((4, 8, 8), dtype=np.float32),
        spacing_zyx=[1, 1, 1],
    )
    labels = np.zeros(
        (4, 8, 8), dtype=np.complex64 if isinstance(invalid, complex) else np.float32
    )
    labels[1, 2, 3] = invalid
    np.savez(tmp_path / "labels.npz", pseudo_labels=labels)
    pd.DataFrame(
        [
            {
                "split": "train",
                "patient_id": "synthetic",
                "series_instance_uid": "fixture",
                "slice_index": 1,
                "depth": 4,
                "height": 8,
                "width": 8,
                "volume_path": "volume.npz",
                "label_volume_path": "labels.npz",
            }
        ]
    ).to_csv(tmp_path / "index.csv", index=False)
    dataset = CT25DDataset(tmp_path / "index.csv")
    with pytest.raises(ValueError, match="finite integer class IDs"):
        dataset[0]


@pytest.mark.parametrize("invalid", [np.nan, np.inf, 1j])
def test_training_preflight_rejects_nonfinite_or_complex_source_voxels(
    tmp_path, invalid
):
    nib = pytest.importorskip("nibabel")
    cases = []
    for index, split in enumerate(("training", "validation", "test")):
        pixels = np.zeros(
            (2, 3, 4),
            dtype=np.complex64 if isinstance(invalid, complex) else np.float32,
        )
        pixels[0, 0, 0] = invalid if index == 0 else index
        path = tmp_path / f"{split}.nii.gz"
        nib.save(nib.Nifti1Image(pixels, np.diag([0.703125, 0.703125, 1.25, 1])), path)
        cases.append(
            {
                "patient_id": f"synthetic{index}",
                "study_id": f"study{index}",
                "split": split,
                "image": path.name,
                "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "annotations_complete": True,
                "nodules": [],
            }
        )
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "lung-nodule-dataset-v1",
                "public_research_approved": True,
                "approved_by": "scripted test only",
                "dataset": "manufactured test images",
                "license": "test fixture",
                "intensity_units": "HU",
                "cases": cases,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="finite real HU"):
        validate_dataset(path, tmp_path)


@pytest.mark.parametrize("issue", ["shape", "nonfinite", "float32_overflow", "complex"])
def test_invalid_workspace_pixels_do_not_reserve_output_and_allow_retry(
    tmp_path, issue
):
    study, hu = detect_study(
        generate_chest(tmp_path / "ct"),
        PhantomDetector(),
        study_id="s",
        patient_alias="synthetic",
    )
    invalid = hu.astype(np.complex64 if issue == "complex" else np.float64)
    if issue == "shape":
        invalid = invalid[:-1]
    elif issue == "nonfinite":
        invalid[0, 0, 0] = np.nan
    elif issue == "float32_overflow":
        invalid[0, 0, 0] = np.finfo(np.float64).max
    else:
        invalid[0, 0, 0] = 1j
    destination = tmp_path / "workspace"
    with pytest.raises(ValueError, match="Pixels"):
        save_workspace(destination, study, invalid)
    assert not destination.exists()
    save_workspace(destination, study, hu)
    _, restored = load_workspace(destination)
    np.testing.assert_array_equal(restored, hu)
