import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import io
import zipfile
import numpy as np
import torch
import pydicom

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from scripts.generate_fixture import generate
from dicom_loader import load_dicom_series
from data.ct25d_dataset import assign_single_case_slice_splits, assert_split_support
from models.unet_small import compute_segmentation_metrics
from preprocessing import (
    run_preprocessing_pipeline,
    restore_prediction_to_source,
    geometry_transform,
)
from config import PreprocessConfig
from deploy.inference_runtime import unzip_series_bytes


class Repairs(unittest.TestCase):
    def test_old_leak_and_new_support(self):
        with self.assertRaises(ValueError):
            assert_split_support(["train", "buffer", "val"])
        for depth in (12, 20, 29, 34, 100):
            assert_split_support(assign_single_case_slice_splits(depth))

    def test_axial_oblique_compressed_and_padding(self):
        for oblique in (False, True):
            for compressed in (False, True):
                with tempfile.TemporaryDirectory() as tmp:
                    generate(tmp, oblique=oblique, compressed=compressed)
                    v = load_dicom_series(tmp)
                    self.assertEqual(v.volume_hu[0, 24, 24], 40)
                    self.assertEqual(
                        v.volume_hu[-1, 24, 24], 58
                    )  # integer stored pixels quantize odd HU
                    self.assertEqual(v.metadata.padding_voxels, 20)
                    self.assertEqual(v.metadata.intensity_hu_range[0], -1000)
                    self.assertNotIn("series_instance_uid", v.metadata.to_dict())

    def test_simpleitk_rescale_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp, compressed=True)
            with patch(
                "dicom_loader._decode_pixels",
                side_effect=lambda ds, path: (
                    (
                        __import__("dicom_loader")._decode_with_simpleitk(path)
                        - float(ds.RescaleIntercept)
                    )
                    / float(ds.RescaleSlope)
                ),
            ):
                self.assertEqual(load_dicom_series(tmp).volume_hu[0, 24, 24], 40)

    def test_reject_mixed_duplicate_and_orientation(self):
        for mode in ("duplicate", "orientation", "series"):
            with tempfile.TemporaryDirectory() as tmp:
                generate(tmp)
                files = sorted(Path(tmp).glob("*.dcm"))
                a = pydicom.dcmread(files[0])
                b = pydicom.dcmread(files[1])
                if mode == "duplicate":
                    b.ImagePositionPatient = a.ImagePositionPatient
                elif mode == "orientation":
                    b.ImageOrientationPatient = [0, 1, 0, 1, 0, 0]
                else:
                    b.SeriesInstanceUID = pydicom.uid.generate_uid()
                b.save_as(files[1], enforce_file_format=True)
                with self.assertRaises(ValueError):
                    load_dicom_series(tmp)

    def test_geometry_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp, oblique=True)
            v = load_dicom_series(tmp)
            r = run_preprocessing_pipeline(
                v.volume_hu,
                v.metadata.spacing_zyx,
                PreprocessConfig(target_spacing_xy_mm=0.5),
            )
            g = geometry_transform(v.metadata, r)
            pred = np.ones(r.processed_volume.shape, dtype=np.uint8)
            restored = restore_prediction_to_source(pred, r, v.volume_hu.shape)
            self.assertEqual(restored.shape, v.volume_hu.shape)
            self.assertEqual(restored[10, 24, 24], 1)
            direction = np.array(g["direction_lps"]).reshape(3, 3)
            bbox = r.crop_bbox_zyx
            expected = np.array(v.metadata.origin_lps) + direction @ (
                np.array([bbox.x_min, bbox.y_min, bbox.z_min])
                * np.array(r.resampled_spacing_zyx)[::-1]
            )
            np.testing.assert_allclose(g["crop_origin_lps"], expected)

    def test_empty_classes_are_not_perfect(self):
        m = compute_segmentation_metrics(
            torch.zeros((1, 4, 4)), torch.zeros((1, 4, 4)), 4
        )
        self.assertEqual(m["dice"], 0)
        self.assertIsNone(m["per_class_dice"]["1"])

    def test_zip_traversal(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as z:
            z.writestr("../escape.dcm", b"bad")
        with self.assertRaises(ValueError):
            unzip_series_bytes(payload.getvalue())

    def test_public_allowlist(self):
        from public_metadata import validate_public_metadata

        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            data = load_dicom_series(tmp).metadata.to_dict()
            self.assertIs(validate_public_metadata(data), data)
            for key in ("PatientID", "study_instance_uid", "institution", "local_path"):
                with self.assertRaises(ValueError):
                    validate_public_metadata({**data, key: "private"})

    def test_epoch_augmentation_and_manifest_guard(self):
        import pandas as pd
        from data.ct25d_dataset import CT25DDataset, RandomIntensityJitter25D

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            np.savez(
                p / "volume.npz",
                volume=np.ones((4, 8, 8), dtype=np.float32) * 0.5,
                spacing_zyx=[1, 1, 1],
            )
            np.savez(
                p / "labels.npz", pseudo_labels=np.zeros((4, 8, 8), dtype=np.uint8)
            )
            frame = pd.DataFrame(
                [
                    {
                        "split": "train",
                        "patient_id": "p1",
                        "series_instance_uid": "sample_001",
                        "slice_index": 1,
                        "depth": 4,
                        "height": 8,
                        "width": 8,
                        "volume_path": "volume.npz",
                        "label_volume_path": "labels.npz",
                    }
                ]
            )
            frame.to_csv(p / "index.csv", index=False)
            a = CT25DDataset(
                p / "index.csv", transforms=RandomIntensityJitter25D(probability=1.0)
            )
            x = a[0]["image"].clone()
            a.set_epoch(1)
            y = a[0]["image"]
            self.assertFalse(torch.equal(x, y))
            a.set_epoch(0)
            self.assertTrue(torch.equal(x, a[0]["image"]))
            (p / "index.sha256").write_text("wrong")
            with self.assertRaises(ValueError):
                CT25DDataset(p / "index.csv")

    def test_calibration_preserves_nll(self):
        from calibration import (
            fit_temperature,
            negative_log_likelihood,
            apply_temperature,
        )

        torch.manual_seed(4)
        logits = torch.randn(2, 4, 8, 8)
        targets = torch.randint(4, (2, 8, 8))
        t = fit_temperature(logits, targets)
        self.assertLessEqual(
            negative_log_likelihood(apply_temperature(logits, t), targets),
            negative_log_likelihood(logits, targets),
        )

    def test_runtime_binding_and_preprocess_mismatch(self):
        from deploy.inference_runtime import (
            verify_runtime_binding,
            verify_preprocessing_contract,
        )
        from types import SimpleNamespace
        from dataclasses import asdict, replace
        import json

        c = {
            "_checkpoint_sha256": "a",
            "preprocessing_contract": json.loads(
                json.dumps(asdict(PreprocessConfig()))
            ),
        }
        verify_preprocessing_contract(c, PreprocessConfig())
        with self.assertRaises(ValueError):
            verify_preprocessing_contract(
                c, replace(PreprocessConfig(), hu_clip_min=-500)
            )
        with self.assertRaises(ValueError):
            verify_runtime_binding(
                c,
                SimpleNamespace(
                    get_modelmeta=lambda: SimpleNamespace(
                        custom_metadata_map={"checkpoint_sha256": "b"}
                    )
                ),
            )

    def test_missing_decode_tags_fail_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            path = next(Path(tmp).glob("*.dcm"))
            ds = pydicom.dcmread(path)
            del ds.BitsAllocated
            ds.save_as(path, enforce_file_format=True)
            with self.assertRaisesRegex(ValueError, "Missing required technical tags"):
                load_dicom_series(tmp)
