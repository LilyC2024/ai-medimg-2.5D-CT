"""Command-line entry points. Inference never downloads or automatically approves."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser(
        "fetch-model", help="Explicitly download pinned official weights and licenses"
    )
    fetch.add_argument("--output", required=True)
    demo = sub.add_parser(
        "demo",
        help="Generated sphere phantom + non-ML fixture finder; leaves review pending",
    )
    demo.add_argument("--output", required=True)
    detect = sub.add_parser("detect", help="Offline pretrained MONAI inference")
    detect.add_argument("--series", required=True)
    detect.add_argument("--model-dir", required=True)
    detect.add_argument(
        "--checkpoint",
        help="Optional local research fine-tuned checkpoint; never a validation claim",
    )
    detect.add_argument("--device", choices=["cpu", "cuda"], required=True)
    detect.add_argument("--threshold", type=float, default=0.15)
    detect.add_argument("--threads", type=int, default=4)
    detect.add_argument(
        "--approval", help="Explicit public research data/protocol approval JSON"
    )
    detect.add_argument("--patient-alias", required=True)
    detect.add_argument("--study-id", required=True)
    detect.add_argument("--output", required=True)
    review = sub.add_parser(
        "review", help="Apply an explicitly authored research reviewer approval JSON"
    )
    review.add_argument("--workspace", required=True)
    review.add_argument("--approval", required=True)
    export = sub.add_parser(
        "export", help="Revalidate approval and export synthetic nodule exchange"
    )
    export.add_argument("--workspace", required=True)
    export.add_argument("--output", required=True)
    a = p.parse_args(argv)
    from lung_nodule.detection import (
        MonaiDetector,
        PhantomDetector,
        detect_study,
        fetch_model,
    )
    from lung_nodule.phantom import generate_chest
    from lung_nodule.workspace import (
        complete_review,
        export_synthetic_exchange,
        save_workspace,
    )

    if a.command == "fetch-model":
        print(json.dumps(fetch_model(a.output), indent=2))
    elif a.command == "demo":
        root = Path(a.output)
        root.mkdir(parents=True, exist_ok=False)
        series = generate_chest(root / "series")
        study, hu = detect_study(
            series,
            PhantomDetector(),
            study_id="phantom-study",
            patient_alias="synthetic",
        )
        save_workspace(root / "workspace", study, hu)
        print(
            f"Workspace: {root / 'workspace'}; review pending. Fixture output is not clinical accuracy."
        )
    elif a.command == "detect":
        import torch

        if a.threads < 1:
            p.error("--threads must be positive")
        torch.set_num_threads(a.threads)
        detector = MonaiDetector(
            a.model_dir, device=a.device, threshold=a.threshold, checkpoint=a.checkpoint
        )
        study, hu = detect_study(
            a.series,
            detector,
            study_id=a.study_id,
            patient_alias=a.patient_alias,
            approval=a.approval,
        )
        save_workspace(a.output, study, hu)
        print(
            f"{len(study.candidates)} candidate(s); review pending. Workspace: {a.output}"
        )
    elif a.command == "review":
        from lung_nodule.contracts import Review

        approval = Review.model_validate_json(Path(a.approval).read_bytes())
        complete_review(a.workspace, approval)
        print(
            "Research reviewer attestation recorded. Report remains educational, not a diagnosis."
        )
    else:
        print(export_synthetic_exchange(a.workspace, a.output))


if __name__ == "__main__":
    main()
