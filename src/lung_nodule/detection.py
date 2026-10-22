"""Offline MONAI RetinaNet inference with explicit source/world coordinate mapping.

Network topology follows the Apache-2.0 MONAI lung_nodule_ct_detection bundle.
Upstream config is stored as provenance, never evaluated as executable Python.
Adapted topology: Copyright (c) MONAI Consortium; Apache License 2.0, see
THIRD_PARTY_NOTICES.md and third_party/MONAI-APACHE-2.0.txt.
"""

from __future__ import annotations

import importlib.metadata
import itertools
import json
from pathlib import Path

import numpy as np

from lung_nodule.contracts import Candidate, ModelProvenance, Study, digest
from lung_nodule.sources import load_sources, sha256

HF_REVISION = "9d6622fda0e52be0a4155fed2e0afb9c17bcd80b"
MODEL_FILES = (
    "models/model.pt",
    "configs/inference.json",
    "configs/metadata.json",
    "LICENSE",
    "docs/data_license.txt",
    "configs/train.json",
    "configs/evaluate.json",
    "configs/logging.conf",
    "scripts/__init__.py",
    "scripts/cocometric_ignite.py",
    "scripts/detection_inferer.py",
    "scripts/detection_saver.py",
    "scripts/evaluator.py",
    "scripts/trainer.py",
    "scripts/utils.py",
    "scripts/warmup_scheduler.py",
)
RECIPE = {
    "architecture": "MONAI RetinaNet resnet50 3D FPN [1,2]",
    "spacing_xyz_mm": [0.703125, 0.703125, 1.25],
    "hu_clip": [-1024.0, 300.0],
    "orientation": "RAS",
    "box_output": "source voxel centers zyx AABB",
    "inference_roi_xyz": [192, 192, 80],
    "nms_iou": 0.22,
    "max_detections": 300,
    "revision": HF_REVISION,
}


def fetch_model(destination):
    """Explicit setup-only download from a fixed official revision; never on inference."""
    import urllib.request

    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for relative in MODEL_FILES:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/MONAI/lung_nodule_ct_detection/resolve/{HF_REVISION}/{relative}"
        with (
            urllib.request.urlopen(url, timeout=60) as source,
            path.open("wb") as output,
        ):
            while chunk := source.read(1024**2):
                output.write(chunk)
        hashes[relative] = sha256(path)
    registration = {
        "schema": "local-monai-model-v1",
        "revision": HF_REVISION,
        "files": hashes,
        "recipe_sha256": digest(RECIPE),
    }
    (destination / "registration.json").write_text(
        json.dumps(registration, indent=2), encoding="utf-8"
    )
    return registration


def verify_model(directory):
    """Reject missing/altered files before deserializing tensor-only weights."""
    directory = Path(directory)
    registration = json.loads(
        (directory / "registration.json").read_text(encoding="utf-8")
    )
    if (
        registration.get("schema") != "local-monai-model-v1"
        or registration.get("revision") != HF_REVISION
        or registration.get("recipe_sha256") != digest(RECIPE)
        or set(registration.get("files", {})) != set(MODEL_FILES)
    ):
        raise ValueError(
            "Model registration/recipe mismatch; run fetch-model into a new directory"
        )
    if any(
        sha256(directory / name) != registration["files"][name] for name in MODEL_FILES
    ):
        raise ValueError("Model artifact hash mismatch")
    return registration


def select_device(requested):
    """No AUTO or silent accelerator fallback. Intel NPU is not CUDA."""
    import torch

    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda:0")
    raise ValueError(
        f"Requested device {requested!r} is unavailable or unsupported; select cpu or a working CUDA device explicitly"
    )


def build_detector(device="cpu", *, score_threshold=0.15):
    """Construct upstream-compatible detector without downloading weights."""
    from monai.apps.detection.networks.retinanet_detector import RetinaNetDetector
    from monai.apps.detection.networks.retinanet_network import (
        RetinaNet,
        resnet_fpn_feature_extractor,
    )
    from monai.apps.detection.utils.anchor_utils import AnchorGeneratorWithAnchorShape
    from monai.networks.nets.resnet import resnet50

    target = select_device(device)
    backbone = resnet50(
        spatial_dims=3,
        n_input_channels=1,
        conv1_t_stride=[2, 2, 1],
        conv1_t_size=[7, 7, 7],
    )
    feature = resnet_fpn_feature_extractor(backbone, 3, False, [1, 2], None)
    network = RetinaNet(
        spatial_dims=3,
        num_classes=1,
        num_anchors=3,
        feature_extractor=feature,
        size_divisible=[16, 16, 8],
        use_list_output=False,
    ).to(target)
    anchors = AnchorGeneratorWithAnchorShape(
        feature_map_scales=[1, 2, 4],
        base_anchor_shapes=[[6, 8, 4], [8, 6, 5], [10, 10, 6]],
    )
    detector = RetinaNetDetector(
        network=network,
        anchor_generator=anchors,
        spatial_dims=3,
        num_classes=1,
        size_divisible=[16, 16, 8],
    )
    detector.set_target_keys(box_key="box", label_key="label")
    detector.set_box_selector_parameters(
        score_thresh=score_threshold,
        topk_candidates_per_level=1000,
        nms_thresh=0.22,
        detections_per_img=300,
    )
    detector.set_sliding_window_inferer(
        roi_size=RECIPE["inference_roi_xyz"],
        overlap=0.25,
        sw_batch_size=1,
        mode="constant",
        device="cpu",
    )
    return detector


def prepare_tensor(hu, geometry):
    """Source zyx HU -> RAS xyz MetaTensor, spacing and window from upstream recipe."""
    import torch
    from monai.data import MetaTensor
    from monai.transforms import Compose, Orientation, ScaleIntensityRange, Spacing

    # Bound resampling before allocating a potentially much larger image.
    estimate = np.prod(
        np.ceil(
            (np.array(geometry.shape_zyx)[::-1] - 1)
            * np.array(geometry.spacing_zyx_mm)[::-1]
            / RECIPE["spacing_xyz_mm"]
        )
        + 1
    )
    if estimate > 256 * 1024**2:
        raise ValueError("Resampled volume exceeds 256Mi voxel allocation limit")
    lps = np.eye(4)
    lps[:3, :3] = np.array(geometry.direction_lps).reshape(3, 3) @ np.diag(
        geometry.spacing_zyx_mm[::-1]
    )
    lps[:3, 3] = geometry.origin_lps_mm
    ras = np.diag([-1.0, -1.0, 1.0, 1.0]) @ lps
    image = MetaTensor(
        torch.from_numpy(np.ascontiguousarray(hu.transpose(2, 1, 0)[None])), affine=ras
    )
    transform = Compose(
        [
            Orientation(axcodes="RAS"),
            Spacing(pixdim=RECIPE["spacing_xyz_mm"], mode="bilinear"),
            ScaleIntensityRange(a_min=-1024, a_max=300, b_min=0, b_max=1, clip=True),
        ]
    )
    return transform(image)


def map_boxes(boxes_xyz, scores, affine_ras, geometry, threshold):
    """Map all eight box corners; never flip only centers or assume axial source."""
    candidates = []
    boxes, scores = np.asarray(boxes_xyz), np.asarray(scores)
    if (
        boxes.shape != (len(scores), 6)
        or not np.isfinite(boxes).all()
        or not np.isfinite(scores).all()
        or np.any((scores < 0) | (scores > 1))
    ):
        raise ValueError("Malformed detector output")
    for box, score in zip(boxes, scores):
        if score < threshold:
            continue
        if np.any(box[:3] >= box[3:]):
            raise ValueError("Invalid detector box extent")
        corners = np.array(list(itertools.product(*zip(box[:3], box[3:]))))
        world_ras = (
            corners @ np.asarray(affine_ras)[:3, :3].T + np.asarray(affine_ras)[:3, 3]
        )
        source = geometry.from_lps(world_ras * [-1, -1, 1])
        lower = np.maximum(source.min(0), 0)
        upper = np.minimum(source.max(0), np.array(geometry.shape_zyx) - 1)
        if np.all(upper > lower):
            candidates.append(
                Candidate(
                    candidate_id=f"N{len(candidates) + 1:03}",
                    box_zyx=tuple(np.r_[lower, upper]),
                    score=float(score),
                )
            )
    return candidates


class MonaiDetector:
    """Local pretrained 3D detector; output scores are not malignancy probabilities."""

    def __init__(self, model_dir, *, device="cpu", threshold=0.15, checkpoint=None):
        import torch

        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must lie in [0,1]")
        verify_model(model_dir)
        self.device, self.threshold = select_device(device), threshold
        self.detector = build_detector(device, score_threshold=threshold)
        weight_path = (
            Path(checkpoint) if checkpoint else Path(model_dir) / "models/model.pt"
        )
        weights = torch.load(weight_path, map_location="cpu", weights_only=True)
        state = weights.get("model", weights)
        self.detector.network.load_state_dict(state, strict=True)
        self.detector.eval()
        self.provenance = ModelProvenance(
            name="MONAI LUNA16 3D RetinaNet"
            + ("; user-supplied research checkpoint" if checkpoint else ""),
            checkpoint_sha256=sha256(weight_path),
            config_sha256=digest(RECIPE),
            execution_device=str(self.device),
            synthetic_fixture=False,
            software_versions={
                p: importlib.metadata.version(p)
                for p in ("torch", "monai", "numpy", "torchvision")
            },
            score_threshold=threshold,
        )

    def predict(self, hu, geometry):
        import torch

        image = prepare_tensor(hu, geometry)
        # Inference precision is FP32 for the reference path. AMP/export are separate experiments.
        with torch.inference_mode():
            output = self.detector(
                [image.to(self.device)],
                use_inferer=bool(
                    np.any(np.array(image.shape[1:]) > RECIPE["inference_roi_xyz"])
                ),
            )[0]
        return map_boxes(
            output["box"].detach().cpu().numpy(),
            output["label_scores"].detach().cpu().numpy(),
            image.affine.cpu().numpy(),
            geometry,
            self.threshold,
        )


class PhantomDetector:
    """Deterministic sphere-fixture finder, NOT a trained lung nodule model."""

    provenance = ModelProvenance(
        name="SYNTHETIC FIXTURE intensity-component finder; not ML",
        checkpoint_sha256=digest("no-trained-weights"),
        config_sha256=digest("phantom:HU>0; lung ROI; min8vox"),
        execution_device="cpu",
        software_versions={"numpy": np.__version__},
        synthetic_fixture=True,
        score_threshold=1.0,
    )

    def predict(self, hu, geometry):
        from scipy.ndimage import label

        if hu.shape != (32, 64, 64):
            raise ValueError(
                "Fixture finder only supports generated chest phantom shape"
            )
        zz, yy, xx = np.mgrid[:32, :64, :64]
        roi = (((xx - 21) / 9) ** 2 + ((yy - 32) / 16) ** 2 < 1) | (
            ((xx - 43) / 9) ** 2 + ((yy - 32) / 16) ** 2 < 1
        )
        components, count = label((hu > 0) & roi)
        candidates = []
        for component in range(1, count + 1):
            points = np.argwhere(components == component)
            if len(points) >= 8 and np.all(points.max(0) > points.min(0)):
                candidates.append(
                    Candidate(
                        candidate_id=f"N{len(candidates) + 1:03}",
                        box_zyx=tuple(np.r_[points.min(0), points.max(0)]),
                        score=1.0,
                    )
                )
        return candidates


def detect_study(series, detector, *, study_id, patient_alias, approval=None):
    hu, geometry, sources, identity, kind, protocol = load_sources(
        series, approval=approval
    )
    if detector.provenance.synthetic_fixture and kind != "generated-synthetic":
        raise ValueError("Fixture detector rejects research patient input")
    study = Study(
        study_id=study_id,
        patient_alias=patient_alias,
        input_kind=kind,
        source_sha256=identity,
        geometry=geometry,
        sources=sources,
        model=detector.provenance,
        candidates=detector.predict(hu, geometry),
        protocol_attestation=protocol,
    )
    return study, hu
