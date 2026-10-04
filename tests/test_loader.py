import tempfile
import unittest
import numpy as np
from scripts.generate_fixture import generate
from dicom_loader import load_dicom_series


class TestDicomLoader(unittest.TestCase):
    def test_loader_returns_expected_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp, depth=12, size=32)
            v = load_dicom_series(tmp)
            self.assertEqual(v.volume_hu.shape, (12, 32, 32))
            self.assertEqual(v.volume_hu.dtype, np.float32)

    def test_z_positions_are_monotonic(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp, depth=12, size=32, oblique=True)
            v = load_dicom_series(tmp)
            self.assertTrue(np.all(np.diff(v.metadata.z_positions) > 0))
