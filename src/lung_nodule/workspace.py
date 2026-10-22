"""Local study snapshots and deterministic reports; human approval binds all content."""

from __future__ import annotations

import html
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image, ImageDraw

from lung_nodule.contracts import Review, Study, digest
from lung_nodule.sources import sha256


def save_workspace(destination, study, hu):
    """Create a new workspace; never overwrite a study or mutate original DICOM."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    if hu.shape != study.geometry.shape_zyx or not np.isfinite(hu).all():
        raise ValueError("Pixels do not match source geometry")
    (destination / "study.json").write_text(
        study.model_dump_json(indent=2), encoding="utf-8"
    )
    np.save(destination / "source.npy", hu.astype(np.float32), allow_pickle=False)
    (destination / "integrity.json").write_text(
        json.dumps(
            {
                "study_digest": digest(study),
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
    """Compose only approved, structured observations; no LLM or cancer inference."""
    review.verify(study)
    lookup = {d.candidate_id: d for d in review.decisions}
    accepted = [
        c for c in study.candidates if lookup[c.candidate_id].decision == "accept"
    ]
    lines = [
        "# Reviewed lung nodule research summary",
        "",
        f"Study: {study.study_id}; subject alias: {study.patient_alias}.",
        f"Input: {study.input_kind}. Acquisition date unavailable. Prior comparison unavailable.",
        f"Reviewer attestation: {html.escape(review.reviewer)}. Local attestation; credentials not independently verified.",
        f"Model: {study.model.name}. Device: {study.model.execution_device}.",
        f"Candidates: {len(study.candidates)} generated; {len(accepted)} accepted for research review.",
        "",
    ]
    if study.model.synthetic_fixture:
        lines += [
            "SYNTHETIC FIXTURE FINDER: this output is a software demonstration, not trained nodule detection.",
            "",
        ]
    if not accepted:
        lines += [
            "No candidates were accepted. This does not establish a normal CT or exclude nodules/cancer.",
            "",
        ]
    for c in study.candidates:
        decision = lookup[c.candidate_id]
        lo, hi = np.array(c.box_zyx[:3]), np.array(c.box_zyx[3:])
        extent_xyz = ((hi - lo) * study.geometry.spacing_zyx_mm)[::-1]
        center = study.geometry.to_lps((lo + hi) / 2)
        lines += [
            f"- {c.candidate_id}: reviewer {decision.decision}; detector score {c.score:.4f} (not malignancy risk).",
            f"  Source-grid box extents x/y/z: {extent_xyz[0]:.2f}/{extent_xyz[1]:.2f}/{extent_xyz[2]:.2f} mm; these are not lesion diameters or segmentation volume.",
            f"  Box center LPS: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}) mm; source slices {int(np.floor(lo[0]))}–{int(np.ceil(hi[0]))} (zero-based).",
        ]
        if decision.caliper:
            lines += [
                f"  Reviewer-placed in-plane caliper: {decision.caliper.length_mm(study.geometry):.2f} mm; slice {decision.caliper.start_zyx[0]:g}."
            ]
        for z in range(int(np.floor(lo[0])), int(np.ceil(hi[0])) + 1):
            lines.append(f"  Evidence slice {z}: SHA-256 {study.sources[z].sha256}.")
    lines += [
        "",
        "Conclusion: accepted entries are candidate image findings requiring clinician interpretation; no malignancy diagnosis or management recommendation is generated.",
        "Coverage and protocol are operator attestations, not automatically established by the model. Missed lesions and false positives remain possible. No laterality/lobar location is inferred from position alone.",
        f"Source-series digest: {study.source_sha256}",
        f"Study snapshot digest: {digest(study)}",
        f"Checkpoint SHA-256: {study.model.checkpoint_sha256}",
        f"Inference recipe SHA-256: {study.model.config_sha256}",
        f"Review digest: {digest(review)}",
        "",
    ]
    return "\n".join(lines)


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


def export_synthetic_exchange(directory, destination):
    """New nodule contract; deliberately distinct from legacy MHCRA v1 tissue masks."""
    directory, destination = Path(directory), Path(destination)
    study, hu = load_workspace(directory)
    if study.input_kind != "generated-synthetic":
        raise ValueError("MHCRA exchange remains synthetic-only")
    report = reviewed_report(directory)
    payload = {
        "schema_version": "mhcra-lung-nodules-v1",
        "synthetic": True,
        "study": study.model_dump(mode="json"),
        "review": json.loads((directory / "review.json").read_text(encoding="utf-8")),
        "report": report,
        "consumer_support": "Requires a nodule-aware consumer; legacy mhcra-imaging-v1 import must reject this format",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("nodules.json", json.dumps(payload, indent=2))
        archive.writestr("report.md", report)
        for c in study.candidates:
            from io import BytesIO

            z = int(round((c.box_zyx[0] + c.box_zyx[3]) / 2))
            buffer = BytesIO()
            overlay_slice(study, hu, z).save(buffer, format="PNG")
            archive.writestr(f"previews/{c.candidate_id}.png", buffer.getvalue())
    return destination
