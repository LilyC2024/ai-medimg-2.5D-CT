"""Offline generated-synthetic nodule jobs for LOVISA; legacy MHCRA entry point, no approval."""

import argparse
from pathlib import Path
import re

from lung_nodule.detection import MonaiDetector, PhantomDetector, detect_study
from lung_nodule.phantom import generate_chest
from lung_nodule.workspace import export_synthetic_exchange, save_workspace


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
        raise argparse.ArgumentTypeError(
            "Use a synthetic ID containing letters, digits, _ or -"
        )
    return value


def generate_bundle(
    destination, patient_id, study_id, *, mode="fixture", model_dir=None, device="cpu"
):
    """Run selected real/fixture detector on generated pixels; export pending v2."""
    identifier(patient_id)
    identifier(study_id)
    if mode not in ("fixture", "pretrained") or (mode == "fixture" and device != "cpu"):
        raise ValueError("Fixture mode is CPU-only; select pretrained for CUDA")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    if mode == "pretrained":
        if model_dir is None:
            raise ValueError(
                "Select an installed local model directory; no automatic download"
            )
        import torch

        torch.set_num_threads(4)
        detector = MonaiDetector(model_dir, device=device)
    else:
        detector = PhantomDetector()
    series = generate_chest(destination / "series")
    study, hu = detect_study(
        series, detector, study_id=study_id, patient_alias=patient_id
    )
    workspace = save_workspace(destination / "workspace", study, hu)
    return export_synthetic_exchange(
        workspace, destination / "exchange/bundle.mhcra.zip", pending=True
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--patient-id", required=True, type=identifier)
    p.add_argument("--study-id", required=True, type=identifier)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--mode", choices=["fixture", "pretrained"], default="fixture")
    p.add_argument("--model-dir")
    p.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    a = p.parse_args()
    result = generate_bundle(
        a.output_dir,
        a.patient_id,
        a.study_id,
        mode=a.mode,
        model_dir=a.model_dir,
        device=a.device,
    )
    print(f"MHCRA_BUNDLE={result}", flush=True)


if __name__ == "__main__":
    main()
