"""Synthetic-only inspection bundles for LOVISA; retained MHCRA tissue-mask interface."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from config import PreprocessConfig
from dicom_loader import load_dicom_series
from deploy.inference_runtime import run_deployment_inference

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {
    "0": "Neither heuristic candidate (not a normality finding)",
    "1": "Brain-like candidate only (unvalidated)",
    "2": "Broad bone candidate only; includes soft tissue (unvalidated)",
    "3": "Heuristic candidate overlap (unvalidated)",
}
COLORS = np.array([[0, 0, 0], [0, 180, 170], [245, 165, 35], [165, 90, 210]], dtype=np.uint8)


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
        raise ValueError("Use a 1–64 character synthetic ID: letters, digits, _ or -")
    return value


def verify_synthetic(series):
    series = Path(series).resolve()
    marker = series.with_name(series.name + ".synthetic.json")
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    actual = {p.name: checksum(p) for p in sorted(series.iterdir()) if p.is_file()}
    if manifest.get("schema") != "ct25d-generated-synthetic-v1" or manifest.get("synthetic") is not True or not actual or manifest.get("files") != actual:
        raise ValueError("Only unchanged generated synthetic series are accepted by the MHCRA bridge")
    return hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest()


def export_bundle(*, series, checkpoint, onnx, destination, patient_id, study_id):
    patient_id, study_id = identifier(patient_id), identifier(study_id)
    source_hash = verify_synthetic(series)
    volume = load_dicom_series(series)
    if volume.volume_hu.shape[0] > 64 or max(volume.volume_hu.shape[1:]) > 256:
        raise ValueError("Workbench demonstration limit: 64 slices, 256 pixels per dimension")
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    result = run_deployment_inference(
        series_dir=series, checkpoint_path=checkpoint, onnx_path=onnx,
        output_dir=destination / "runtime", preprocess_config=PreprocessConfig(),
        save_overlays=False, enable_postprocess=False, validate_onnx=True,
    )
    # Use the exported SOURCE grid, never processed-grid counts, for measurements.
    with np.load(result.output_paths.mask_volume_path, allow_pickle=False) as data:
        labels = data["predicted_labels"]
        spacing = data["spacing_zyx"].astype(float)
        origin = data["origin_lps"].astype(float)
        direction = data["direction_lps"].astype(float)
    if labels.shape != volume.volume_hu.shape or not np.isin(labels, [0, 1, 2, 3]).all():
        raise ValueError("Source-grid mask contract mismatch")
    artifacts = []

    def artifact(path, role, slice_index=None):
        item = {"path": path.relative_to(destination).as_posix(), "role": role,
                "sha256": checksum(path), "size_bytes": path.stat().st_size,
                "slice_index": slice_index}
        artifacts.append(item)

    artifact(result.output_paths.mask_volume_path, "mask")
    previews = destination / "previews"
    previews.mkdir()
    gray = (np.clip((volume.volume_hu + 200) / 1200, 0, 1) * 255).astype(np.uint8)
    for z in range(len(labels)):
        rgb = np.repeat(gray[z, :, :, None], 3, axis=2)
        overlay = rgb.copy()
        selected = labels[z] != 0
        overlay[selected] = (0.55 * rgb[selected] + 0.45 * COLORS[labels[z][selected]]).astype(np.uint8)
        for suffix, pixels, role in [("source", rgb, "source_preview"), ("overlay", overlay, "overlay_preview")]:
            path = previews / f"{z:03d}-{suffix}.png"
            Image.fromarray(pixels).save(path)
            artifact(path, role, z)
    counts = [int((labels == i).sum()) for i in range(4)]
    bundle = {
        "schema_version": "mhcra-imaging-v1", "synthetic": True,
        "patient_id": patient_id, "study_id": study_id, "job_id": uuid.uuid4().hex,
        "acquisition_date": None, "processed_at": datetime.now(timezone.utc).isoformat(),
        "source_series_sha256": source_hash,
        "checkpoint_sha256": checksum(checkpoint), "onnx_sha256": checksum(onnx),
        "model_name": "UNetSmall", "classes": CLASSES,
        "geometry": {"shape_zyx": list(labels.shape), "spacing_zyx_mm": spacing.tolist(),
                     "origin_lps": origin.tolist(), "direction_lps": direction.tolist()},
        "voxel_counts": counts,
        "candidate_volumes_mm3": [float(c * np.prod(spacing)) for c in counts],
        "postprocessing_enabled": False,
        "onnx_parity_passed": bool(result.report["onnx_validation"]["within_tolerance"]),
        "uncertainty_mean": float(result.report["uncertainty_summary"]["mean"]),
        "artifacts": artifacts,
        "limitations": "Heuristic model outputs; no verified anatomy, lesion diagnosis or clinical confidence. Synthetic demonstration only. Acquisition date unavailable. Source-grid candidate volumes are research measurements.",
    }
    manifest = destination / "bundle.json"
    manifest.write_text(json.dumps(bundle, indent=2, allow_nan=False), encoding="utf-8")
    archive = destination / "bundle.mhcra.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(manifest, "bundle.json")
        for item in artifacts:
            z.write(destination / item["path"], item["path"])
    return archive


def synthetic_demo(destination, patient_id, study_id):
    from scripts.generate_fixture import generate
    from scripts.prepare_case import prepare

    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    series = generate(destination / "series")
    prepare(series, destination / "processed")
    subprocess.run([
        sys.executable, str(ROOT / "scripts/train.py"),
        "--index-path", str(destination / "processed/index.csv"),
        "--output-dir", str(destination / "training"), "--model-dir", str(destination / "models"),
        "--epochs", "12", "--image-size", "32,32", "--base-channels", "4",
    ], cwd=ROOT, check=True)
    return export_bundle(series=series, checkpoint=destination / "models/best.pt",
                         onnx=destination / "model.onnx", destination=destination / "exchange",
                         patient_id=patient_id, study_id=study_id)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--demo", action="store_true", help="Generate and train a tiny synthetic smoke model")
    p.add_argument("--patient-id", required=True, type=identifier)
    p.add_argument("--study-id", required=True, type=identifier)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--series-dir")
    p.add_argument("--checkpoint")
    p.add_argument("--onnx-path")
    a = p.parse_args()
    if a.demo:
        result = synthetic_demo(a.output_dir, a.patient_id, a.study_id)
    else:
        if not all((a.series_dir, a.checkpoint, a.onnx_path)):
            p.error("Supply --demo or --series-dir, --checkpoint and --onnx-path")
        result = export_bundle(series=a.series_dir, checkpoint=a.checkpoint, onnx=a.onnx_path,
                               destination=a.output_dir, patient_id=a.patient_id, study_id=a.study_id)
    print(f"MHCRA_BUNDLE={result}", flush=True)


if __name__ == "__main__":
    main()
