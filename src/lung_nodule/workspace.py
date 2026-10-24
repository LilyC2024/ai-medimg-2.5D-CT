"""Local study snapshots and deterministic reports; human approval binds all content."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from lung_nodule.contracts import Review, Study, digest
from lung_nodule.sources import sha256


def save_workspace(destination, study, hu, *, inference_region=None):
    """Create a new workspace; never overwrite a study or mutate original DICOM."""
    destination = Path(destination)
    hu = np.asarray(hu)
    if (
        hu.shape != study.geometry.shape_zyx
        or not np.issubdtype(hu.dtype, np.number)
        or np.iscomplexobj(hu)
        or not np.isfinite(hu).all()
        or np.any(np.abs(hu) > np.finfo(np.float32).max)
    ):
        raise ValueError(
            "Pixels must match source geometry and contain finite real float32-representable values"
        )
    # Validate before reserving the output name. Invalid inputs must remain
    # retryable and must never persist an unreadable float32 source snapshot.
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "study.json").write_text(
        study.model_dump_json(indent=2), encoding="utf-8"
    )
    np.save(destination / "source.npy", hu.astype(np.float32), allow_pickle=False)
    (destination / "integrity.json").write_text(
        json.dumps(
            {
                "study_digest": digest(study),
                **(
                    {"inference_region_zyx": list(inference_region)}
                    if inference_region is not None
                    else {}
                ),
                "source_npy_sha256": sha256(destination / "source.npy"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return destination


def load_workspace(directory):
    """Verify dimensions/header before array allocation and check snapshot integrity."""
    directory = Path(directory)
    if (directory / "study.json").stat().st_size > 2 * 1024**2:
        raise ValueError("Study JSON exceeds limit")
    study = Study.model_validate_json((directory / "study.json").read_bytes())
    integrity = json.loads((directory / "integrity.json").read_text(encoding="utf-8"))
    path = directory / "source.npy"
    if integrity.get("study_digest") != digest(study) or integrity.get(
        "source_npy_sha256"
    ) != sha256(path):
        raise ValueError("Workspace content changed; review/inference must be repeated")
    if path.stat().st_size > int(np.prod(study.geometry.shape_zyx)) * 4 + 1024:
        raise ValueError("Source array exceeds declared shape")
    with path.open("rb") as handle:
        version = np.lib.format.read_magic(handle)
        if version not in ((1, 0), (2, 0)):
            raise ValueError("Unsupported NPY version")
        reader = (
            np.lib.format.read_array_header_1_0
            if version == (1, 0)
            else np.lib.format.read_array_header_2_0
        )
        shape, fortran, dtype = reader(handle)
        if shape != study.geometry.shape_zyx or fortran or dtype != np.dtype("float32"):
            raise ValueError("Array header does not match source contract")
        expected = handle.tell() + int(np.prod(shape)) * 4
        if path.stat().st_size != expected:
            raise ValueError("Unexpected array payload length")
    pixels = np.load(path, allow_pickle=False)
    if not np.isfinite(pixels).all():
        raise ValueError("Invalid source pixels")
    return study, pixels


def overlay_slice(study, hu, z, *, annotated=True, calipers=()):
    """Lung-window source pixels plus source-grid candidate boxes; no altered anatomy."""
    if not 0 <= z < len(hu):
        raise ValueError("Slice outside source volume")
    gray = (np.clip((hu[z] + 1000) / 1400, 0, 1) * 255).astype(np.uint8)
    image = Image.fromarray(gray).convert("RGB")
    if annotated:
        draw = ImageDraw.Draw(image)
        for c in study.candidates:
            a, b = np.array(c.box_zyx[:3]), np.array(c.box_zyx[3:])
            if a[0] <= z <= b[0]:
                draw.rectangle((a[2], a[1], b[2], b[1]), outline="#ffb020", width=1)
                draw.text((a[2], max(0, a[1] - 10)), c.candidate_id, fill="#ffb020")
    draw = ImageDraw.Draw(image)
    for caliper in calipers:
        length = caliper.length_mm(study.geometry)
        a, b = caliper.start_zyx, caliper.end_zyx
        if a[0] == z:
            draw.line((a[2], a[1], b[2], b[1]), fill="#00e5ff", width=1)
            for point in (a, b):
                draw.ellipse(
                    (point[2] - 1, point[1] - 1, point[2] + 1, point[1] + 1),
                    fill="#00e5ff",
                )
            draw.text((b[2] + 2, b[1]), f"{length:.1f}mm", fill="#00e5ff")
    return image


def report_text(study, review):
    """Use the shared deterministic CT/MHCRA report contract."""
    from lung_nodule.contracts import research_report

    return research_report(study, review)


def complete_review(directory, review):
    """Re-read source snapshot immediately before exporting a completed report."""
    directory = Path(directory)
    study, _ = load_workspace(directory)
    report = report_text(study, review)
    # Approval is persisted last; a partial write never grants completion.
    (directory / "report.md").write_text(report, encoding="utf-8")
    (directory / "review.json").write_text(
        review.model_dump_json(indent=2), encoding="utf-8"
    )
    return report


def reviewed_report(directory):
    """Recompose on every download; stale/tampered report files cannot confer approval."""
    directory = Path(directory)
    study, _ = load_workspace(directory)
    review = Review.model_validate_json((directory / "review.json").read_bytes())
    return report_text(study, review)


def _export_exchange(
    directory,
    destination,
    *,
    pending=False,
    research=None,
    original_study=None,
    crop_origin_zyx=None,
    inference_region=None,
    signing_key=None,
):
    """Export verified v2 source/annotation bundle; pending mode grants no approval.

    With ``signing_key`` (an Ed25519 key file path) the archive carries a producer
    signature. CT performance is always declared unmeasured: no FROC or
    false-positive evaluation exists for this detector.
    """
    from datetime import datetime, timezone
    from io import BytesIO
    from uuid import uuid4

    from lung_nodule.exchange_contract import PENDING_REPORT, read_exchange, wire_pixels

    directory, destination = Path(directory), Path(destination)
    study, hu = load_workspace(directory)
    if study.input_kind != "generated-synthetic" and research is None:
        raise ValueError("MHCRA exchange remains synthetic-only")
    review_path = directory / "review.json"
    review = (
        Review.model_validate_json(review_path.read_bytes())
        if review_path.exists()
        else None
    )
    if review is not None:
        report = report_text(study, review)
    elif pending:
        report = PENDING_REPORT
    else:
        raise ValueError(
            "Explicit review required; pending exports are only an unreviewed workbench proposal"
        )
    files = {
        "source.npy": (directory / "source.npy").read_bytes(),
        "producer/report.md": report.encode("utf-8"),
    }
    items: list[dict[str, Any]] = [
        {"path": "source.npy", "role": "source_volume", "slice_index": None},
        {"path": "producer/report.md", "role": "producer_report", "slice_index": None},
    ]
    calipers = [d.caliper for d in review.decisions if d.caliper] if review else []
    for index in range(len(hu)):
        source, overlay = wire_pixels(study, hu, index, calipers=calipers)
        for role, pixels in (("source_preview", source), ("overlay_preview", overlay)):
            path = f"previews/{index:03d}-{role}.png"
            buffer = BytesIO()
            Image.fromarray(pixels).save(buffer, format="PNG")
            files[path] = buffer.getvalue()
            items.append({"path": path, "role": role, "slice_index": index})
    import hashlib

    for a in items:
        data = files[a["path"]]
        a.update(sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data))
    payload = {
        "schema_version": "lovisa-ct-research-v3"
        if research is not None
        else "mhcra-lung-nodules-v2",
        "synthetic": research is None,
        "patient_id": study.patient_alias,
        "study_id": study.study_id,
        "job_id": uuid4().hex,
        "acquisition_date": None,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": "producer_reviewed" if review else "pending_review",
        "study": study.model_dump(mode="json"),
        "producer_review": review.model_dump(mode="json") if review else None,
        "artifacts": items,
    }
    if research is not None:
        payload.update(
            research=research,
            original_study=original_study.model_dump(mode="json"),
            crop_origin_zyx=crop_origin_zyx,
            inference_region_zyx=inference_region,
        )
    archive_bytes = BytesIO()
    with zipfile.ZipFile(archive_bytes, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("bundle.json", json.dumps(payload, indent=2, allow_nan=False))
        for name, data in files.items():
            archive.writestr(name, data)
    data = archive_bytes.getvalue()
    if signing_key is not None:
        from lung_nodule.producer_signature import load_private_key, sign_archive

        data = sign_archive(data, load_private_key(signing_key), "lovisa-ct")
    read_exchange(
        data, study.patient_alias
    )  # fail before publishing incomplete/invalid output
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        output.write(data)
    return destination


def export_synthetic_exchange(
    directory, destination, *, pending=False, signing_key=None
):
    """Legacy synthetic-v2 export; public studies require the explicit research API."""
    return _export_exchange(
        directory, destination, pending=pending, signing_key=signing_key
    )


def export_research_exchange(
    directory,
    destination,
    *,
    patient_id,
    research,
    crop_origin_zyx,
    shape_zyx,
    signing_key=None,
):
    """Export an unreviewed, bounded, source-mapped public CT excerpt to a composite case.

    No resampling or inferred anatomy is introduced. Whole-source study metadata and
    hashes remain in the manifest; absent scan pixels are never claimed to be covered.
    """
    import tempfile

    from lung_nodule.contracts import Geometry, SourceSlice
    from lung_nodule.exchange_contract import PublicResearchSource

    original, hu = load_workspace(directory)
    integrity = json.loads((Path(directory) / "integrity.json").read_text())
    inference_region = integrity.get("inference_region_zyx", [0, 0, 0, *hu.shape])
    provenance = PublicResearchSource.model_validate(research)
    if original.input_kind != "approved-public-research":
        raise ValueError("Research export requires verified public source workspace")
    if provenance.original_sha256 != sha256(Path(directory) / "source.npy"):
        raise ValueError("Research source array hash mismatch")
    offset, shape = np.array(crop_origin_zyx), np.array(shape_zyx)
    if (
        offset.shape != (3,)
        or shape.shape != (3,)
        or not np.issubdtype(offset.dtype, np.integer)
        or not np.issubdtype(shape.dtype, np.integer)
        or np.any(offset < 0)
        or np.any(shape < [2, 1, 1])
        or np.any(shape > [64, 256, 256])
        or np.any(offset + shape > np.array(hu.shape))
    ):
        raise ValueError("Invalid bounded source crop")
    geometry = Geometry.model_validate(
        dict(
            original.geometry.model_dump(),
            shape_zyx=tuple(int(x) for x in shape),
            origin_lps_mm=tuple(original.geometry.to_lps(offset)),
        )
    )
    sources = [
        SourceSlice.model_validate(dict(s.model_dump(), index=i))
        for i, s in enumerate(original.sources[offset[0] : offset[0] + shape[0]])
    ]
    candidates = []
    for c in original.candidates:
        lo, hi = np.array(c.box_zyx[:3]), np.array(c.box_zyx[3:])
        if np.all(lo >= offset) and np.all(hi <= offset + shape - 1):
            candidates.append(
                c.model_copy(update={"box_zyx": tuple(np.r_[lo - offset, hi - offset])})
            )
    values = dict(
        original.model_dump(),
        patient_alias=patient_id,
        geometry=geometry,
        sources=sources,
        candidates=candidates,
        source_sha256=digest(
            {
                "geometry": geometry.model_dump(mode="json"),
                "sources": [s.model_dump(mode="json") for s in sources],
            }
        ),
    )
    study = Study.model_validate(values)
    excerpt = hu[tuple(slice(int(o), int(o + n)) for o, n in zip(offset, shape))].copy()
    with tempfile.TemporaryDirectory() as temp:
        workspace = Path(temp) / "excerpt"
        save_workspace(workspace, study, excerpt)
        return _export_exchange(
            workspace,
            destination,
            pending=True,
            research=provenance.model_dump(mode="json"),
            original_study=original,
            crop_origin_zyx=tuple(int(x) for x in offset),
            inference_region=inference_region,
            signing_key=signing_key,
        )
