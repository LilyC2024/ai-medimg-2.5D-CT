import json
import tempfile
import unittest
import zipfile
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

from config import PreprocessConfig
from deploy.mhcra_bridge import export_bundle, identifier, verify_synthetic, checksum
from models.unet_small import UNetSmall
from scripts.generate_fixture import generate


class BridgeTests(unittest.TestCase):
    def test_synthetic_bundle_identity_geometry_artifacts_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            series = generate(p / "series", depth=12, size=32, oblique=True)
            model = UNetSmall(base_channels=2)
            torch.save({"model_config": {"in_channels": 3, "num_classes": 4, "base_channels": 2},
                        "preprocessing_contract": json.loads(json.dumps(asdict(PreprocessConfig()))),
                        "state_dict": model.state_dict(), "resize": {"height": 32, "width": 32}}, p / "model.pt")
            archive = export_bundle(series=series, checkpoint=p / "model.pt", onnx=p / "model.onnx",
                                    destination=p / "exchange", patient_id="synthetic-checklist", study_id="study-001")
            with zipfile.ZipFile(archive) as z:
                m = json.loads(z.read("bundle.json"))
                self.assertEqual(m["patient_id"], "synthetic-checklist")
                self.assertIsNone(m["acquisition_date"])
                self.assertTrue(m["synthetic"] and m["onnx_parity_passed"])
                self.assertFalse(m["postprocessing_enabled"])
                self.assertEqual(m["geometry"]["shape_zyx"], [12, 32, 32])
                self.assertEqual(m["geometry"]["origin_lps"], [10., 20., 30.])
                self.assertEqual(sum(m["voxel_counts"]), 12 * 32 * 32)
                self.assertEqual(len(m["artifacts"]), 25)
                for a in m["artifacts"]:
                    self.assertEqual(a["sha256"], checksum(p / "exchange" / a["path"]))
                    self.assertEqual(len(z.read(a["path"])), a["size_bytes"])
                with np.load(p / "exchange/runtime/prediction_mask.npz", allow_pickle=False) as d:
                    self.assertEqual(m["voxel_counts"], [int((d["predicted_labels"] == i).sum()) for i in range(4)])
            (series / "001.dcm").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                verify_synthetic(series)

    def test_requires_generator_proof_and_safe_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            generate(p / "series", depth=12, size=32)
            (p / "series.synthetic.json").unlink()
            with self.assertRaises(FileNotFoundError):
                verify_synthetic(p / "series")
            with self.assertRaises(ValueError):
                identifier("../patient")
            with self.assertRaises(ValueError):
                generate(p / "series")
