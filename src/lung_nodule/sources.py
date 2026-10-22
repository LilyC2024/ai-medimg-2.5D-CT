"""Load immutable synthetic or explicitly approved public research sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pydicom

from dicom_loader import load_dicom_series
from lung_nodule.contracts import Geometry, SourceSlice, digest


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024**2), b""):
            h.update(chunk)
    return h.hexdigest()


def load_sources(directory, *, approval=None):
    """Read one series twice-bound to byte hashes; no filenames or raw UIDs in output."""
    directory = Path(directory).resolve()
    marker = directory.with_name(directory.name + ".synthetic.json")
    files = sorted(p for p in directory.iterdir() if p.is_file())
    before = {p.name: sha256(p) for p in files}
    if marker.exists():
        data = json.loads(marker.read_text())
        if data.get("schema") not in ("lung-nodule-phantom-v1", "ct25d-generated-synthetic-v1") or data.get("synthetic") is not True or data.get("files") != before:
            raise ValueError("Synthetic source marker mismatch")
        kind, protocol = "generated-synthetic", "synthetic-phantom"
    else:
        if approval is None:
            raise ValueError("Public research data requires an explicit local approval file; clinical input is unsupported")
        data = json.loads(Path(approval).read_text())
        if set(data) != {"public_research_only", "dataset", "license", "approved_by", "protocol"} or data["public_research_only"] is not True or not all(isinstance(data[k], str) and data[k].strip() for k in ("dataset", "license", "approved_by")) or data["protocol"] != "adult-noncontrast-chest-complete":
            raise ValueError("Invalid public research/protocol approval")
        kind, protocol = "approved-public-research", data["protocol"]
    volume = load_dicom_series(directory, max_voxels=128 * 1024**2)
    if len(files) < 2:
        raise ValueError("A CT volume requires at least two source slices")
    records, studies, frames = [], set(), set()
    normal = np.array(volume.metadata.direction_lps).reshape(3, 3)[:, 2]
    for path in files:
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        if not ds.get("SOPInstanceUID") or not ds.get("StudyInstanceUID"):
            raise ValueError("Source requires SOP and study identity")
        studies.add(str(ds.StudyInstanceUID))
        frames.add(str(ds.get("FrameOfReferenceUID", "")))
        records.append((float(np.array(ds.ImagePositionPatient) @ normal), before[path.name],
                        hashlib.sha256(str(ds.SOPInstanceUID).encode()).hexdigest()))
    if len(studies) != 1 or len(frames) != 1 or before != {p.name: sha256(p) for p in files}:
        raise ValueError("Source changed or mixes study/frame identities")
    if kind == "approved-public-research" and (volume.metadata.spacing_zyx[0] > 2.5 or max(volume.metadata.spacing_zyx[1:]) > 1.5):
        raise ValueError("Unsupported research resolution: require <=2.5mm slices and <=1.5mm pixels")
    geometry = Geometry(shape_zyx=volume.volume_hu.shape, spacing_zyx_mm=volume.metadata.spacing_zyx,
                        origin_lps_mm=volume.metadata.origin_lps, direction_lps=volume.metadata.direction_lps)
    sources = [SourceSlice(index=i, sha256=h, sop_uid_sha256=u) for i, (_, h, u) in enumerate(sorted(records))]
    identity = digest({"geometry": geometry.model_dump(mode="json"),
                       "sources": [s.model_dump(mode="json") for s in sources]})
    return volume.volume_hu, geometry, sources, identity, kind, protocol
