"""Allowlisted public metadata; aliasing alone is not DICOM anonymization."""

import json
import re
from pathlib import Path

ALLOWED = {
    "modality",
    "slice_count",
    "rows",
    "columns",
    "spacing_zyx",
    "orientation_lps",
    "rescale_slope_range",
    "rescale_intercept_range",
    "z_positions",
    "validation_messages",
    "origin_lps",
    "direction_lps",
    "padding_voxels",
    "intensity_hu_range",
    "case_alias",
    "schema_version",
}


def validate_public_metadata(data):
    if set(data) - ALLOWED:
        raise ValueError("Fields outside public allowlist.")
    if data.get("schema_version") != 1 or not re.fullmatch(
        r"sample_[0-9]{3}", data.get("case_alias", "")
    ):
        raise ValueError("Invalid schema or case alias.")
    if data.get("modality") != "CT":
        raise ValueError("Only CT metadata supported.")
    for name in ("slice_count", "rows", "columns"):
        if type(data.get(name)) is not int or data[name] <= 0:
            raise ValueError("Invalid dimensions.")
    for name, count in (
        ("spacing_zyx", 3),
        ("orientation_lps", 6),
        ("origin_lps", 3),
        ("direction_lps", 9),
        ("intensity_hu_range", 2),
        ("rescale_slope_range", 2),
        ("rescale_intercept_range", 2),
    ):
        value = data.get(name)
        if (
            not isinstance(value, (list, tuple))
            or len(value) != count
            or any(
                type(v) not in (int, float) or not __import__("math").isfinite(v)
                for v in value
            )
        ):
            raise ValueError("Invalid numeric technical field.")
    if min(data["spacing_zyx"]) <= 0:
        raise ValueError("Spacing must be positive.")
    raw = json.dumps(data)
    if re.search(r"[A-Za-z]:[\\/]|/Users/|/home/|\\\\", raw):
        raise ValueError("Machine-specific path.")
    if any(not isinstance(v, (int, float)) for v in data.get("z_positions", [])):
        raise ValueError("Invalid positions.")
    if data.get("validation_messages") != []:
        raise ValueError("Public free text requires separate review.")
    return data
