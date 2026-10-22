"""Small reproducible chest-like phantom with known spheres, never clinical validation."""

import json
from pathlib import Path

import numpy as np

from lung_nodule.sources import sha256


def generate_chest(destination, *, seed=7, lesion=True):
    """Generate 32x64x64 DICOM, 1.5x1x1mm spacing and optional synthetic sphere."""
    from pydicom.dataset import FileDataset, FileMetaDataset
    from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

    directory = Path(destination)
    directory.mkdir(parents=True, exist_ok=False)
    study_uid, series_uid, frame_uid = generate_uid(), generate_uid(), generate_uid()
    zz, yy, xx = np.mgrid[:32, :64, :64]
    body = ((xx - 32) / 28) ** 2 + ((yy - 32) / 24) ** 2 < 1
    lungs = (((xx - 21) / 10) ** 2 + ((yy - 32) / 17) ** 2 < 1) | (
        ((xx - 43) / 10) ** 2 + ((yy - 32) / 17) ** 2 < 1
    )
    target = ((zz - 16) * 1.5) ** 2 + (yy - 30) ** 2 + (xx - 22) ** 2 <= 4**2
    hu = np.where(body, 35.0, -1000.0)
    hu[lungs] = -800.0
    if lesion:
        hu[target] = 60.0
    hu += np.random.default_rng(seed).normal(0, 8, hu.shape)
    for z in range(32):
        path = directory / f"{31 - z:03d}.dcm"
        meta = FileMetaDataset()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        ds = FileDataset(str(path), {}, file_meta=meta, preamble=bytes(128))
        ds.SOPClassUID, ds.SOPInstanceUID = (
            CTImageStorage,
            meta.MediaStorageSOPInstanceUID,
        )
        ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.FrameOfReferenceUID = (
            study_uid,
            series_uid,
            frame_uid,
        )
        ds.PatientID, ds.Modality, ds.InstanceNumber = (
            "GENERATED-SYNTHETIC",
            "CT",
            z + 1,
        )
        ds.Rows = ds.Columns = 64
        ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        ds.PixelSpacing = [1.0, 1.0]
        ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, "MONOCHROME2"
        ds.BitsAllocated = ds.BitsStored = 16
        ds.HighBit, ds.PixelRepresentation = 15, 1
        ds.ImagePositionPatient = [10.0, 20.0, 30.0 + 1.5 * z]
        ds.SliceThickness = 1.5
        ds.BodyPartExamined = "CHEST"
        ds.RescaleSlope, ds.RescaleIntercept = 1.0, 0.0
        ds.PixelData = hu[z].astype(np.int16).tobytes()
        ds.save_as(path, enforce_file_format=True)
    directory.with_name(directory.name + ".synthetic.json").write_text(
        json.dumps(
            {
                "schema": "lung-nodule-phantom-v1",
                "synthetic": True,
                "files": {p.name: sha256(p) for p in sorted(directory.iterdir())},
            }
        ),
        encoding="utf-8",
    )
    return directory
