import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from scripts.generate_fixture import generate
from models.unet_small import UNetSmall


class TestDeploymentSmoke(unittest.TestCase):
    def test_cli_inference_runs_end_to_end_and_batch_invariance(self):
        torch.manual_seed(13)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            generate(p / "series", depth=12, size=32, oblique=True)
            model = UNetSmall(base_channels=2)
            torch.save(
                {
                    "model_config": {
                        "in_channels": 3,
                        "num_classes": 4,
                        "base_channels": 2,
                    },
                    "state_dict": model.state_dict(),
                    "resize": {"height": 32, "width": 32},
                    "temperature": 1.0,
                },
                p / "model.pt",
            )
            labels = []
            for batch in (1, 3):
                command = [
                    sys.executable,
                    str(ROOT / "deploy/cli_infer.py"),
                    "--series-dir",
                    str(p / "series"),
                    "--checkpoint",
                    str(p / "model.pt"),
                    "--onnx-path",
                    str(p / "model.onnx"),
                    "--output-dir",
                    str(p / f"out{batch}"),
                    "--batch-size",
                    str(batch),
                    "--output-formats",
                    "mask",
                ]
                result = subprocess.run(
                    command, cwd=tmp, capture_output=True, text=True
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(
                    (p / f"out{batch}" / "day7_onnx_validation.json").read_text()
                )
                self.assertTrue(report["within_tolerance"])
                with np.load(p / f"out{batch}" / "prediction_mask.npz") as data:
                    self.assertEqual(data["predicted_labels"].shape, (12, 32, 32))
                    self.assertEqual(tuple(data["origin_lps"]), (10, 20, 30))
                    labels.append(data["predicted_labels"])
            np.testing.assert_array_equal(*labels)
