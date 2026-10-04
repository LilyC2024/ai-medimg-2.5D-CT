import io
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
import torch
from fastapi.testclient import TestClient
from deploy.app import app
from deploy.inference_runtime import export_checkpoint_to_onnx
from models.unet_small import UNetSmall
from scripts.generate_fixture import generate


class ServiceTests(unittest.TestCase):
    def test_unavailable_model(self):
        with patch.dict(
            os.environ, {"CT25D_CHECKPOINT": "absent.pt", "CT25D_ONNX": "absent.onnx"}
        ):
            with TestClient(app) as client:
                self.assertEqual(client.get("/health").status_code, 503)
                self.assertEqual(
                    client.post(
                        "/predict", files={"dicom_zip": ("bad.zip", b"bad")}
                    ).status_code,
                    503,
                )

    def test_valid_malformed_oversized_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            generate(p / "series", depth=12, size=32)
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
                },
                p / "model.pt",
            )
            export_checkpoint_to_onnx(p / "model.pt", p / "model.onnx")
            payload = io.BytesIO()
            with zipfile.ZipFile(payload, "w") as z:
                for file in (p / "series").iterdir():
                    z.write(file, file.name)
            before = set(Path(tempfile.gettempdir()).glob("ct25d_*"))
            with patch.dict(
                os.environ,
                {
                    "CT25D_CHECKPOINT": str(p / "model.pt"),
                    "CT25D_ONNX": str(p / "model.onnx"),
                },
            ):
                with TestClient(app) as client:
                    self.assertEqual(client.get("/health").status_code, 200)
                    result = client.post(
                        "/predict",
                        files={"dicom_zip": ("series.zip", payload.getvalue())},
                    )
                    self.assertEqual(result.status_code, 200, result.text[:1000])
                    with zipfile.ZipFile(io.BytesIO(result.content)) as archive:
                        self.assertEqual(
                            set(archive.namelist()),
                            {"prediction_mask.npz", "technical.json"},
                        )
                    self.assertEqual(
                        client.post(
                            "/predict", files={"dicom_zip": ("bad.zip", b"bad")}
                        ).status_code,
                        422,
                    )
                    self.assertEqual(
                        client.post(
                            "/predict",
                            files={
                                "dicom_zip": ("big.zip", b"0" * (64 * 1024 * 1024 + 1))
                            },
                        ).status_code,
                        413,
                    )
            self.assertEqual(set(Path(tempfile.gettempdir()).glob("ct25d_*")), before)
