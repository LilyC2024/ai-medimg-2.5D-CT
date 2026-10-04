"""Generate synthetic CT; no source patient data or copied headers."""

from pathlib import Path
import argparse
import numpy as np
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, CTImageStorage, generate_uid


def generate(destination, depth=20, size=48, oblique=False, compressed=False):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    series, study = generate_uid(), generate_uid()
    row = np.array([1.0, 0.0, 0.0])
    col = np.array([0.0, 0.0, 1.0] if oblique else [0.0, 1.0, 0.0])
    normal = np.cross(row, col)
    yy, xx = np.mgrid[:size, :size]
    r = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2)
    for i in range(depth):
        meta = FileMetaDataset()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        ds = FileDataset(
            str(destination / f"{depth - i:03d}.dcm"),
            {},
            file_meta=meta,
            preamble=bytes(128),
        )
        ds.SOPClassUID = CTImageStorage
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
        ds.SeriesInstanceUID = series
        ds.StudyInstanceUID = study
        ds.PatientID = "SYNTHETIC"
        ds.Modality = "CT"
        ds.Rows = size
        ds.Columns = size
        ds.ImageOrientationPatient = [*row, *col]
        ds.ImagePositionPatient = list(np.array([10.0, 20.0, 30.0]) + normal * i * 5)
        ds.PixelSpacing = [1.0, 1.0]
        ds.SliceThickness = 5.0
        ds.InstanceNumber = i + 1
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 1
        ds.RescaleSlope = 2.0
        ds.RescaleIntercept = -1000.0
        ds.PixelPaddingValue = -2000
        hu = np.where(r < size * 0.34, 40 + i, np.where(r < size * 0.4, 700, -1000))
        pixels = ((hu + 1000) / 2).astype(np.int16)
        pixels[0, 0] = -2000
        ds.PixelData = pixels.tobytes()
        if compressed:
            from pydicom.uid import RLELossless

            ds.compress(RLELossless)
        ds.save_as(destination / f"{depth - i:03d}.dcm", enforce_file_format=True)
    return destination


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("destination")
    p.add_argument("--oblique", action="store_true")
    p.add_argument("--compressed", action="store_true")
    a = p.parse_args()
    generate(a.destination, oblique=a.oblique, compressed=a.compressed)
