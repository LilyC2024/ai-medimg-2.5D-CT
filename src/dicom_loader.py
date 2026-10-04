from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pydicom


@dataclass(frozen=True)
class SeriesMetadata:
    series_instance_uid: str
    modality: str
    slice_count: int
    rows: int
    columns: int
    spacing_zyx: tuple
    orientation_lps: tuple
    rescale_slope_range: tuple
    rescale_intercept_range: tuple
    z_positions: list
    validation_messages: list
    origin_lps: tuple
    direction_lps: tuple
    padding_voxels: int
    intensity_hu_range: tuple

    def to_dict(self):
        result = asdict(self)
        # Original UIDs stay in memory, never in public technical reports.
        result.pop("series_instance_uid")
        result["case_alias"] = "sample_001"
        result["schema_version"] = 1
        from public_metadata import validate_public_metadata

        validate_public_metadata(result)
        return result


@dataclass(frozen=True)
class DicomVolume:
    volume_hu: np.ndarray
    metadata: SeriesMetadata


def _decode_with_simpleitk(path):
    import SimpleITK as sitk

    arr = sitk.GetArrayFromImage(sitk.ReadImage(str(path)))
    if arr.shape[0] != 1:
        raise ValueError("Multi-frame DICOM is unsupported.")
    return arr[0].astype(np.float32)


def _decode_pixels(dataset, path):
    # pydicom returns stored pixels, including compressed decoding; rescale once below.
    try:
        return dataset.pixel_array.astype(np.float32)
    except (RuntimeError, NotImplementedError):
        # GDCM/SimpleITK applies modality rescale. Invert it here to keep one contract.
        slope = float(dataset.RescaleSlope)
        return (_decode_with_simpleitk(path) - float(dataset.RescaleIntercept)) / slope


def load_dicom_series(series_dir):
    path = Path(series_dir).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(
            "Missing CT series; see docs/data.md for acquisition instructions."
        )
    files = sorted(p for p in path.iterdir() if p.is_file())
    if not files:
        raise ValueError("Empty series directory.")
    if len(files) > 512:
        raise ValueError("Series exceeds 512 slices.")
    records = []
    required = (
        "SeriesInstanceUID",
        "Modality",
        "Rows",
        "Columns",
        "ImageOrientationPatient",
        "ImagePositionPatient",
        "PixelSpacing",
        "RescaleSlope",
        "RescaleIntercept",
        "PixelData",
        "SamplesPerPixel",
        "PhotometricInterpretation",
        "BitsAllocated",
        "BitsStored",
        "HighBit",
        "PixelRepresentation",
    )
    for file in files:
        ds = pydicom.dcmread(file)
        missing = [key for key in required if key not in ds]
        if missing:
            raise ValueError(f"Missing required technical tags: {missing}")
        if (
            max(int(ds.Rows), int(ds.Columns)) > 1024
            or min(int(ds.Rows), int(ds.Columns)) < 1
            or int(ds.Rows) * int(ds.Columns) * len(files) > 64 * 1024 * 1024
        ):
            raise ValueError("Series dimensions exceed supported limits.")
        if (
            ds.PhotometricInterpretation not in ("MONOCHROME1", "MONOCHROME2")
            or ds.Modality != "CT"
            or int(ds.get("NumberOfFrames", 1)) != 1
            or int(ds.get("SamplesPerPixel", 1)) != 1
        ):
            raise ValueError("Only single-frame monochrome CT is supported.")
        if "LOCALIZER" in str(ds.get("ImageType", "")).upper():
            raise ValueError("Localizers are unsupported.")
        orientation = np.asarray(ds.ImageOrientationPatient, dtype=float)
        position = np.asarray(ds.ImagePositionPatient, dtype=float)
        spacing = np.asarray(ds.PixelSpacing, dtype=float)
        if orientation.shape != (6,) or position.shape != (3,) or spacing.shape != (2,):
            raise ValueError("Malformed geometry.")
        row, col = orientation[:3], orientation[3:]
        if (
            not np.isfinite(np.r_[orientation, position, spacing]).all()
            or np.any(spacing <= 0)
            or not np.isclose(np.linalg.norm(row), 1, atol=1e-5)
            or not np.isclose(np.linalg.norm(col), 1, atol=1e-5)
            or not np.isclose(row @ col, 0, atol=1e-5)
        ):
            raise ValueError("Invalid DICOM direction or spacing.")
        slope, intercept = float(ds.RescaleSlope), float(ds.RescaleIntercept)
        if not np.isfinite([slope, intercept]).all() or slope == 0:
            raise ValueError("Invalid rescale values.")
        if records:
            first = records[0][1]
            if ds.SeriesInstanceUID != first.SeriesInstanceUID or (
                ds.Rows,
                ds.Columns,
            ) != (first.Rows, first.Columns):
                raise ValueError("Mixed series or dimensions.")
            if not np.allclose(
                orientation, first.ImageOrientationPatient, atol=1e-5
            ) or not np.allclose(spacing, first.PixelSpacing, atol=1e-6):
                raise ValueError("Inconsistent orientation or pixel spacing.")
        normal = np.cross(row, col)
        records.append((float(position @ normal), ds, file, position))
    records.sort(key=lambda r: r[0])
    positions = np.array([r[0] for r in records])
    differences = np.diff(positions)
    if len(differences):
        if np.any(differences <= 1e-5) or not np.allclose(
            differences, np.median(differences), rtol=1e-3, atol=1e-3
        ):
            raise ValueError("Duplicate or nonuniform slice positions.")
        z = float(np.median(differences))
    else:
        z = float(records[0][1].get("SliceThickness", 0))
    if z <= 0:
        raise ValueError("Missing positive slice spacing.")
    first = records[0][1]
    orientation = np.array(first.ImageOrientationPatient, dtype=float)
    normal = np.cross(orientation[:3], orientation[3:])
    origin = records[0][3]
    for projection, ds, file, position in records:
        expected = origin + normal * (projection - positions[0])
        if not np.allclose(position, expected, atol=0.01):
            raise ValueError("In-plane slice displacement/gantry tilt is unsupported.")
    planes, valid_values, slopes, intercepts = [], [], [], []
    padding_count = 0
    for _, ds, file, _ in records:
        try:
            stored = _decode_pixels(ds, file)
        except (RuntimeError, AttributeError, NotImplementedError) as exc:
            raise ValueError(
                "Unable to decode CT pixels; provide valid supported DICOM or install codecs extra."
            ) from exc
        if stored.shape != (int(ds.Rows), int(ds.Columns)):
            raise ValueError("Decoded dimensions disagree with header.")
        padding = np.zeros(stored.shape, dtype=bool)
        if "PixelPaddingValue" in ds:
            lo, hi = sorted(
                (
                    float(ds.PixelPaddingValue),
                    float(ds.get("PixelPaddingRangeLimit", ds.PixelPaddingValue)),
                )
            )
            padding = (stored >= lo) & (stored <= hi)
        hu = stored * float(ds.RescaleSlope) + float(ds.RescaleIntercept)
        valid_values.append(hu[~padding])
        padding_count += int(padding.sum())
        hu[padding] = -1000.0  # Outside ROI; excluded from descriptive statistics.
        planes.append(hu)
        slopes.append(float(ds.RescaleSlope))
        intercepts.append(float(ds.RescaleIntercept))
    values = np.concatenate(valid_values)
    if not len(values):
        raise ValueError("No nonpadding pixels.")
    direction = np.column_stack((orientation[:3], orientation[3:], normal))
    metadata = SeriesMetadata(
        str(first.SeriesInstanceUID),
        "CT",
        len(records),
        int(first.Rows),
        int(first.Columns),
        (z, *map(float, first.PixelSpacing)),
        tuple(map(float, orientation)),
        (min(slopes), max(slopes)),
        (min(intercepts), max(intercepts)),
        positions.tolist(),
        [],
        tuple(map(float, origin)),
        tuple(map(float, direction.ravel())),
        padding_count,
        (float(values.min()), float(values.max())),
    )
    return DicomVolume(np.stack(planes).astype(np.float32), metadata)


def write_metadata_json(metadata, output_path):
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
