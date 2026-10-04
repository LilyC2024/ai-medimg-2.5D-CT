"""Versioned, sanitized preprocessing and pseudo-label manifest CLI."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import sys
import numpy as np
from config import PreprocessConfig, SegmentationConfig
from dicom_loader import load_dicom_series
from preprocessing import (
    run_preprocessing_pipeline,
    save_npz_volume,
    geometry_transform,
)
from baselines.classical_seg import generate_classical_masks
from data.ct25d_dataset import (
    CT25DCase,
    assign_single_case_slice_splits,
    build_case_index,
    CT25DDataset,
)


def prepare(series, destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    volume = load_dicom_series(series)
    config = PreprocessConfig()
    teacher = SegmentationConfig()
    result = run_preprocessing_pipeline(
        volume.volume_hu, volume.metadata.spacing_zyx, config
    )
    teacher_result = generate_classical_masks(result.cropped_volume_hu, teacher)
    labels = teacher_result.pseudo_labels_3d
    save_npz_volume(
        result.processed_volume,
        result.resampled_spacing_zyx,
        destination / "volume.npz",
    )
    np.savez_compressed(destination / "labels.npz", pseudo_labels=labels)
    splits = assign_single_case_slice_splits(len(labels))
    case = CT25DCase(
        "subject_001",
        "study_001",
        "sample_001",
        Path(series),
        destination / "volume.npz",
        destination / "labels.npz",
        None,
        result.resampled_spacing_zyx,
        labels.shape,
        "subject_001",
    )
    frame = build_case_index([case], {"subject_001": "train"}, {"subject_001": splits})
    frame["volume_path"] = "volume.npz"
    frame["label_volume_path"] = "labels.npz"
    frame["series_dir"] = "source-series"
    frame.to_csv(destination / "index.csv", index=False)
    checksum = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "case_alias": "sample_001",
        "pipeline_version": "0.8.0",
        "geometry": geometry_transform(volume.metadata, result),
        "preprocessing": asdict(config),
        "pseudo_label_method": {
            "version": "classical-v1",
            "parameters": asdict(teacher),
            "selected_candidate": teacher_result.brain_selection,
        },
        "shape_zyx": list(labels.shape),
        "checksums": {
            name: checksum(destination / name)
            for name in ("volume.npz", "labels.npz", "index.csv")
        },
        "split_counts": {name: splits.count(name) for name in set(splits)},
        "excluded_centers": [i for i, s in enumerate(splits) if s == "buffer"],
        "class_counts": {str(i): int((labels == i).sum()) for i in range(4)},
        "quality_flags": [
            "empty_class_" + str(i) for i in range(1, 4) if not np.any(labels == i)
        ],
        "limitations": "Single-series demonstration; no unseen-patient claim; visual review and permissions remain separate.",
    }
    manifest["preprocessing_fingerprint"] = hashlib.sha256(
        json.dumps(
            {"geometry": manifest["geometry"], "config": asdict(config)}, sort_keys=True
        ).encode()
    ).hexdigest()
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (destination / "index.sha256").write_text(checksum(destination / "index.csv"))
    (destination / "technical.json").write_text(
        json.dumps(volume.metadata.to_dict(), indent=2)
    )
    # Original filenames/UIDs and header metadata are never published here.
    (destination / "source_checksums.local.json").write_text(
        json.dumps(
            {
                "case_alias": "sample_001",
                "files": [
                    {"ordinal": i, "sha256": checksum(p)}
                    for i, p in enumerate(sorted(Path(series).iterdir()))
                    if p.is_file()
                ],
            },
            indent=2,
        )
    )
    for split in ("train", "val", "test"):
        dataset = CT25DDataset(destination / "index.csv", split=split)
        for i in range(len(dataset)):
            dataset[i]
    print(
        json.dumps(
            {
                "shape": list(labels.shape),
                "split_counts": manifest["split_counts"],
                "quality_flags": manifest["quality_flags"],
            }
        )
    )
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--series-dir", required=True)
    p.add_argument("--output-dir", "--processed-dir", dest="output_dir", required=True)
    a = p.parse_args()
    prepare(a.series_dir, a.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
