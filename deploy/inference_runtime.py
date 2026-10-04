from __future__ import annotations

import io
import hashlib
import json
import os

os.environ.setdefault("MPLBACKEND", "Agg")
import sys
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[1]

from config import PreprocessConfig  # noqa: E402
from data.ct25d_dataset import build_25d_stack  # noqa: E402
from dicom_loader import load_dicom_series  # noqa: E402
from calibration import apply_temperature  # noqa: E402
from models.unet_small import UNetSmall, compute_segmentation_metrics  # noqa: E402
from preprocessing import (
    run_preprocessing_pipeline,
    save_nifti_volume,
    restore_prediction_to_source,
    geometry_transform,
)  # noqa: E402
from robustness import (  # noqa: E402
    LabelPostprocessConfig,
    compute_entropy_uncertainty,
    postprocess_multiclass_prediction,
    summarize_uncertainty,
)
from visualization import save_day7_prediction_overlays  # noqa: E402


@dataclass(frozen=True)
class RuntimePaths:
    mask_volume_path: Path
    overlay_dir: Path
    report_path: Path
    preprocess_report_path: Path
    validation_report_path: Path | None


@dataclass(frozen=True)
class DeploymentResult:
    prediction_volume: np.ndarray
    probabilities_czyx: np.ndarray
    processed_volume: np.ndarray
    processed_spacing_zyx: tuple[float, float, float]
    raw_slice_count: int
    output_paths: RuntimePaths
    report: dict[str, Any]


def set_deterministic_runtime(num_threads: int) -> None:
    threads = max(int(num_threads), 1)
    os.environ["OMP_NUM_THREADS"] = str(threads)
    os.environ["MKL_NUM_THREADS"] = str(threads)
    np.random.seed(13)
    torch.manual_seed(13)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(threads)


def load_checkpoint(checkpoint_path: str | Path) -> dict[str, Any]:
    path = Path(checkpoint_path).expanduser().resolve()
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    checkpoint["_checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return checkpoint


def build_model_from_checkpoint(checkpoint: dict[str, Any]) -> UNetSmall:
    if (
        checkpoint["model_config"].get("in_channels") != 3
        or checkpoint["model_config"].get("num_classes") != 4
    ):
        raise ValueError("Unsupported checkpoint class/channel contract.")
    model = UNetSmall(**checkpoint["model_config"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model


def export_checkpoint_to_onnx(
    checkpoint_path: str | Path,
    onnx_path: str | Path,
    *,
    opset_version: int = 17,
) -> Path:
    checkpoint = load_checkpoint(checkpoint_path)
    model = build_model_from_checkpoint(checkpoint)
    resize = checkpoint["resize"]
    sample = torch.randn(
        1,
        int(checkpoint["model_config"]["in_channels"]),
        int(resize["height"]),
        int(resize["width"]),
        dtype=torch.float32,
    )
    destination = Path(onnx_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with torch.no_grad():
        torch.onnx.export(
            model,
            sample,
            str(destination),
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes={
                "input": {0: "batch"},
                "logits": {0: "batch"},
            },
            opset_version=int(opset_version),
            do_constant_folding=True,
            dynamo=False,
        )
    import onnx

    graph = onnx.load(str(destination))
    onnx.helper.set_model_props(
        graph,
        {
            "checkpoint_sha256": checkpoint["_checkpoint_sha256"],
            "pipeline_version": "0.8.0",
        },
    )
    onnx.checker.check_model(graph)
    onnx.save(graph, str(destination))
    return destination


def load_and_preprocess_series(
    series_dir: str | Path,
    preprocess_config: PreprocessConfig,
) -> tuple[np.ndarray, tuple[float, float, float], dict[str, Any]]:
    read_start = time.perf_counter()
    dicom_volume = load_dicom_series(series_dir)
    read_seconds = time.perf_counter() - read_start
    preprocess_start = time.perf_counter()
    result = run_preprocessing_pipeline(
        volume_hu=dicom_volume.volume_hu,
        spacing_zyx=dicom_volume.metadata.spacing_zyx,
        preprocess_config=preprocess_config,
    )
    preprocess_report = {
        "geometry": geometry_transform(dicom_volume.metadata, result),
        "timings": {
            "dicom_read_seconds": read_seconds,
            "preprocessing_seconds": time.perf_counter() - preprocess_start,
        },
        "case_alias": "sample_001",
        "raw_shape_zyx": [int(v) for v in dicom_volume.volume_hu.shape],
        "processed_shape_zyx": [int(v) for v in result.processed_volume.shape],
        "input_spacing_zyx_mm": [float(v) for v in result.input_spacing_zyx],
        "processed_spacing_zyx_mm": [float(v) for v in result.resampled_spacing_zyx],
        "crop_bbox_zyx": result.crop_bbox_zyx.to_dict(),
        "dicom_validation_messages": list(dicom_volume.metadata.validation_messages),
        "preprocess_config": asdict(preprocess_config),
    }
    return (
        result.processed_volume.astype(np.float32, copy=False),
        tuple(float(v) for v in result.resampled_spacing_zyx),
        preprocess_report,
    )


def build_input_stack_volume(processed_volume: np.ndarray) -> np.ndarray:
    stacks = [
        build_25d_stack(processed_volume, center_index=index)
        for index in range(int(processed_volume.shape[0]))
    ]
    return np.stack(stacks, axis=0).astype(np.float32, copy=False)


def _resize_stack_batch(batch: np.ndarray, height: int, width: int) -> np.ndarray:
    tensor = torch.from_numpy(batch.astype(np.float32, copy=False))
    resized = F.interpolate(
        tensor, size=(height, width), mode="bilinear", align_corners=False
    )
    return resized.numpy().astype(np.float32, copy=False)


def _apply_temperature_numpy(logits: np.ndarray, temperature: float) -> np.ndarray:
    return logits.astype(np.float32, copy=False) / max(float(temperature), 1e-3)


def _softmax_numpy(logits: np.ndarray) -> np.ndarray:
    logits = logits.astype(np.float32, copy=False)
    logits = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(logits)
    return exp / np.clip(exp.sum(axis=1, keepdims=True), a_min=1e-6, a_max=None)


def validate_onnx_equivalence(
    checkpoint_path: str | Path,
    onnx_path: str | Path,
    sample_batch: np.ndarray,
    *,
    num_threads: int = 1,
    temperature: float = 1.0,
) -> dict[str, Any]:
    checkpoint = load_checkpoint(checkpoint_path)
    model = build_model_from_checkpoint(checkpoint)
    session = create_onnx_session(onnx_path, num_threads=num_threads)
    verify_runtime_binding(checkpoint, session)

    with torch.no_grad():
        torch_logits = (
            apply_temperature(model(torch.from_numpy(sample_batch)), temperature)
            .cpu()
            .numpy()
        )
    onnx_logits = _apply_temperature_numpy(
        session.run(["logits"], {"input": sample_batch.astype(np.float32, copy=False)})[
            0
        ],
        temperature,
    )

    diff = np.abs(torch_logits - onnx_logits)
    probability_diff = np.abs(
        _softmax_numpy(torch_logits) - _softmax_numpy(onnx_logits)
    )
    return {
        "sample_batch_shape": [int(v) for v in sample_batch.shape],
        "max_abs_diff": float(diff.max()),
        "mean_abs_diff": float(diff.mean()),
        "max_prob_diff": float(probability_diff.max()),
        "mean_prob_diff": float(probability_diff.mean()),
        "mask_agreement": float(
            np.mean(torch_logits.argmax(1) == onnx_logits.argmax(1))
        ),
        "within_tolerance": bool(
            np.allclose(
                _softmax_numpy(torch_logits),
                _softmax_numpy(onnx_logits),
                atol=1e-4,
                rtol=1e-3,
            )
            and np.mean(torch_logits.argmax(1) == onnx_logits.argmax(1)) >= 0.999
        ),
    }


def create_onnx_session(
    onnx_path: str | Path, *, num_threads: int = 1
) -> ort.InferenceSession:
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = max(int(num_threads), 1)
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return ort.InferenceSession(
        str(Path(onnx_path).expanduser().resolve()),
        sess_options=session_options,
        providers=["CPUExecutionProvider"],
    )


def verify_runtime_binding(checkpoint, session):
    if (
        session.get_modelmeta().custom_metadata_map.get("checkpoint_sha256")
        != checkpoint["_checkpoint_sha256"]
    ):
        raise ValueError(
            "ONNX/checkpoint provenance mismatch; export the matching checkpoint."
        )


def verify_preprocessing_contract(checkpoint, config):
    expected = checkpoint.get("preprocessing_contract")
    if expected is None:
        raise ValueError(
            "Historical checkpoint lacks preprocessing contract; retrain the corrected baseline."
        )
    if json.loads(json.dumps(asdict(config))) != expected:
        raise ValueError("Input preprocessing differs from the checkpoint contract.")


def run_onnx_segmentation(
    session: ort.InferenceSession,
    stack_volume: np.ndarray,
    *,
    model_height: int,
    model_width: int,
    batch_size: int = 1,
    original_hw: tuple[int, int],
    temperature: float = 1.0,
) -> np.ndarray:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive.")

    outputs: list[np.ndarray] = []
    for start in range(0, int(stack_volume.shape[0]), int(batch_size)):
        batch = stack_volume[start : start + batch_size]
        resized = _resize_stack_batch(batch, model_height, model_width)
        logits = _apply_temperature_numpy(
            session.run(["logits"], {"input": resized})[0], temperature
        )
        probabilities = _softmax_numpy(logits)
        if tuple(probabilities.shape[-2:]) != tuple(original_hw):
            resized_probabilities = F.interpolate(
                torch.from_numpy(probabilities),
                size=original_hw,
                mode="bilinear",
                align_corners=False,
            ).numpy()
            probabilities = resized_probabilities / np.clip(
                resized_probabilities.sum(axis=1, keepdims=True),
                a_min=1e-6,
                a_max=None,
            )
        outputs.append(probabilities.astype(np.float32, copy=False))
    return np.concatenate(outputs, axis=0).astype(np.float32, copy=False)


from evaluation import apply_day6_postprocess


def save_prediction_volume(
    prediction_volume: np.ndarray,
    *,
    spacing_zyx: tuple[float, float, float],
    output_path: str | Path,
    output_format: str,
) -> Path:
    destination = Path(output_path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "npz":
        np.savez_compressed(
            destination,
            predicted_labels=prediction_volume.astype(np.uint8),
            spacing_zyx=np.asarray(spacing_zyx, dtype=np.float32),
        )
        return destination
    if output_format == "nii.gz":
        return save_nifti_volume(
            prediction_volume.astype(np.float32), spacing_zyx, destination
        )
    raise ValueError(f"Unsupported output format: {output_format}")


def run_deployment_inference(
    *,
    series_dir: str | Path,
    checkpoint_path: str | Path,
    onnx_path: str | Path,
    output_dir: str | Path,
    preprocess_config: PreprocessConfig,
    batch_size: int = 1,
    num_threads: int = 1,
    export_onnx: bool = False,
    validate_onnx: bool = True,
    mask_output_format: str = "npz",
    save_overlays: bool = True,
    enable_postprocess: bool = True,
    runtime_session=None,
    runtime_checkpoint=None,
) -> DeploymentResult:
    total_start = time.perf_counter()
    if export_onnx or not Path(onnx_path).expanduser().resolve().exists():
        export_checkpoint_to_onnx(checkpoint_path, onnx_path)

    set_deterministic_runtime(num_threads)
    checkpoint = (
        runtime_checkpoint
        if runtime_checkpoint is not None
        else load_checkpoint(checkpoint_path)
    )
    verify_preprocessing_contract(checkpoint, preprocess_config)
    model_height = int(checkpoint["resize"]["height"])
    model_width = int(checkpoint["resize"]["width"])
    temperature = float(checkpoint.get("temperature", 1.0))

    processed_volume, spacing_zyx, preprocess_report = load_and_preprocess_series(
        series_dir, preprocess_config
    )
    stack_start = time.perf_counter()
    stack_volume = build_input_stack_volume(processed_volume)
    stack_seconds = time.perf_counter() - stack_start
    sample_batch = _resize_stack_batch(
        stack_volume[
            np.unique(
                np.linspace(
                    0, len(stack_volume) - 1, min(5, len(stack_volume)), dtype=int
                )
            )
        ],
        model_height,
        model_width,
    )

    validation_report: dict[str, Any] | None = None
    if validate_onnx:
        validation_report = validate_onnx_equivalence(
            checkpoint_path=checkpoint_path,
            onnx_path=onnx_path,
            sample_batch=sample_batch,
            num_threads=num_threads,
            temperature=temperature,
        )

    if validation_report is not None and not validation_report["within_tolerance"]:
        raise RuntimeError("ONNX parity gate failed.")
    session = (
        runtime_session
        if runtime_session is not None
        else create_onnx_session(onnx_path, num_threads=num_threads)
    )
    verify_runtime_binding(checkpoint, session)
    inference_start = time.perf_counter()
    probabilities_bchw = run_onnx_segmentation(
        session,
        stack_volume,
        model_height=model_height,
        model_width=model_width,
        batch_size=batch_size,
        original_hw=(int(processed_volume.shape[1]), int(processed_volume.shape[2])),
        temperature=temperature,
    )
    inference_seconds = time.perf_counter() - inference_start
    post_start = time.perf_counter()
    if enable_postprocess:
        prediction_volume = apply_day6_postprocess(probabilities_bchw)
    else:
        prediction_volume = probabilities_bchw.argmax(axis=1).astype(np.uint8)

    post_seconds = time.perf_counter() - post_start
    export_start = time.perf_counter()
    uncertainty = compute_entropy_uncertainty(
        np.transpose(probabilities_bchw, (1, 0, 2, 3))
    )
    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    mask_extension = "npz" if mask_output_format == "npz" else "nii.gz"
    mask_volume_path = output_root / f"prediction_mask.{mask_extension}"
    cropped_prediction = prediction_volume
    geometry = preprocess_report["geometry"]
    from preprocessing import BoundingBox3D, PreprocessResult

    result_geometry = PreprocessResult(
        np.zeros(geometry["resampled_shape_zyx"], dtype=np.uint8),
        processed_volume,
        processed_volume,
        tuple(geometry["source_spacing_zyx"]),
        tuple(geometry["target_spacing_zyx"]),
        BoundingBox3D(**geometry["crop_bounds_inclusive_exclusive"]),
    )
    restored = restore_prediction_to_source(
        prediction_volume, result_geometry, geometry["source_shape_zyx"]
    )
    saved_mask_path = save_prediction_volume(
        restored,
        spacing_zyx=tuple(geometry["source_spacing_zyx"]),
        output_path=mask_volume_path,
        output_format=mask_output_format,
    )

    if mask_output_format == "npz":
        np.savez_compressed(
            saved_mask_path,
            predicted_labels=restored,
            spacing_zyx=geometry["source_spacing_zyx"],
            origin_lps=geometry["source_origin_lps"],
            direction_lps=geometry["direction_lps"],
        )
    else:
        import SimpleITK as sitk

        image = sitk.GetImageFromArray(restored)
        image.SetSpacing(tuple(geometry["source_spacing_zyx"][::-1]))
        image.SetOrigin(tuple(geometry["source_origin_lps"]))
        image.SetDirection(tuple(geometry["direction_lps"]))
        sitk.WriteImage(image, str(saved_mask_path))
    overlay_dir = output_root / "overlays"
    saved_overlays = []
    if save_overlays:
        saved_overlays = save_day7_prediction_overlays(
            center_slices=processed_volume,
            predicted_labels=prediction_volume,
            output_dir=overlay_dir,
            uncertainty=uncertainty,
        )

    report = {
        "timings": {
            **preprocess_report["timings"],
            "stack_creation_seconds": stack_seconds,
            "inference_seconds": inference_seconds,
            "postprocessing_seconds": post_seconds,
            "export_seconds": time.perf_counter() - export_start,
            "end_to_end_seconds": time.perf_counter() - total_start,
        },
        "model_resize": {
            "height": model_height,
            "width": model_width,
            "input_interpolation": "bilinear align_corners=False",
            "inverse_label_interpolation": "nearest",
        },
        "case_alias": "sample_001",
        "checkpoint_path": str(Path(checkpoint_path).expanduser().resolve()),
        "onnx_path": str(Path(onnx_path).expanduser().resolve()),
        "slice_count": int(restored.shape[0]),
        "processed_slice_count": int(prediction_volume.shape[0]),
        "source_shape_zyx": list(restored.shape),
        "processed_shape_zyx": [int(v) for v in processed_volume.shape],
        "processed_spacing_zyx_mm": [float(v) for v in spacing_zyx],
        "batch_size": int(batch_size),
        "num_threads": int(num_threads),
        "mask_output_format": mask_output_format,
        "mask_volume_path": str(saved_mask_path),
        "overlay_dir": str(overlay_dir),
        "overlay_count": int(len(saved_overlays)),
        "postprocessing_enabled": bool(enable_postprocess),
        "calibration": checkpoint.get("calibration", {"temperature": temperature}),
        "uncertainty_summary": summarize_uncertainty(
            uncertainty, foreground_mask=prediction_volume > 0
        ),
        "onnx_validation": validation_report,
        "class_voxel_counts": {
            str(class_index): int((prediction_volume == class_index).sum())
            for class_index in range(int(probabilities_bchw.shape[1]))
        },
    }
    report_path = output_root / "day7_infer_report.json"
    preprocess_report_path = output_root / "day7_preprocess_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    preprocess_report_path.write_text(
        json.dumps(preprocess_report, indent=2), encoding="utf-8"
    )

    validation_report_path: Path | None = None
    if validation_report is not None:
        validation_report_path = output_root / "day7_onnx_validation.json"
        validation_report_path.write_text(
            json.dumps(validation_report, indent=2), encoding="utf-8"
        )

    return DeploymentResult(
        prediction_volume=prediction_volume,
        probabilities_czyx=np.transpose(probabilities_bchw, (1, 0, 2, 3)).astype(
            np.float32, copy=False
        ),
        processed_volume=processed_volume,
        processed_spacing_zyx=spacing_zyx,
        raw_slice_count=int(restored.shape[0]),
        output_paths=RuntimePaths(
            mask_volume_path=saved_mask_path,
            overlay_dir=overlay_dir,
            report_path=report_path,
            preprocess_report_path=preprocess_report_path,
            validation_report_path=validation_report_path,
        ),
        report=report,
    )


def load_reference_labels(processed_dir: str | Path) -> np.ndarray | None:
    candidate = (
        Path(processed_dir).expanduser().resolve()
        / "pseudo_labels"
        / "pseudo_labels_3d.npz"
    )
    if not candidate.exists():
        return None
    with np.load(candidate) as data:
        return data["pseudo_labels"].astype(np.uint8)


def attach_reference_metrics(
    report: dict[str, Any],
    prediction_volume: np.ndarray,
    reference_labels: np.ndarray | None,
) -> dict[str, Any]:
    if reference_labels is None:
        return report
    metrics = compute_segmentation_metrics(
        torch.from_numpy(prediction_volume.astype(np.int64)),
        torch.from_numpy(reference_labels.astype(np.int64)),
        num_classes=4,
    )
    updated = dict(report)
    updated["reference_metrics_against_day3_pseudo_labels"] = metrics
    return updated


def unzip_series_bytes(payload: bytes) -> Path:
    import shutil

    if len(payload) > 64 * 1024 * 1024:
        raise ValueError("Upload exceeds 64 MiB.")
    temp_dir = Path(tempfile.mkdtemp(prefix="ct25d_dicom_"))
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            files = [entry for entry in archive.infolist() if not entry.is_dir()]
            if (
                not files
                or len(files) > 512
                or sum(entry.file_size for entry in files) > 256 * 1024 * 1024
            ):
                raise ValueError("Archive is empty or exceeds decoded limits.")
            for entry in archive.infolist():
                name = entry.filename.replace("\\", "/")
                if (
                    name.startswith("/")
                    or ":" in name
                    or ".." in Path(name).parts
                    or ((entry.external_attr >> 16) & 0o170000) == 0o120000
                ):
                    raise ValueError("Unsafe archive member.")
                target = (temp_dir / name).resolve()
                if not target.is_relative_to(temp_dir.resolve()):
                    raise ValueError("Archive path escapes temporary root.")
            archive.extractall(temp_dir)
        directories = {p.parent for p in temp_dir.rglob("*") if p.is_file()}
        if len(directories) != 1:
            raise ValueError("Provide exactly one DICOM series directory.")
        return directories.pop()
    except Exception:
        shutil.rmtree(temp_dir)
        raise
