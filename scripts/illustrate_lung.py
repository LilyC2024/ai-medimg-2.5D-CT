"""Reproduce a figure from generated source pixels and fixture annotations, not patient images."""

from pathlib import Path
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lung_nodule.contracts import Caliper
from lung_nodule.detection import PhantomDetector, detect_study
from lung_nodule.phantom import generate_chest
from lung_nodule.workspace import overlay_slice


def main():
    with tempfile.TemporaryDirectory() as tmp:
        study, hu = detect_study(
            generate_chest(Path(tmp) / "ct"),
            PhantomDetector(),
            study_id="figure",
            patient_alias="synthetic",
        )
        fig, axes = plt.subplots(1, 3, figsize=(12, 4.3), facecolor="#101a2b")
        caliper = Caliper(start_zyx=(16, 30, 18), end_zyx=(16, 30, 26))
        images = [
            overlay_slice(study, hu, 16, annotated=False),
            overlay_slice(study, hu, 16),
            overlay_slice(study, hu, 16, calipers=[caliper]),
        ]
        for axis, image, title in zip(
            axes,
            images,
            [
                "1. Source CT phantom",
                "2. Candidate annotation",
                "3. Source-plane caliper",
            ],
        ):
            axis.imshow(image)
            axis.set_title(title, color="white", fontsize=12, pad=12)
            axis.axis("off")
        fig.suptitle(
            "Local lung nodule research workflow", color="white", fontsize=18, y=0.99
        )
        fig.text(
            0.5,
            0.035,
            "Generated phantom + deterministic fixture finder. 8 mm caliper illustration; no clinical accuracy or human approval claimed.",
            ha="center",
            color="#c7d5ec",
            fontsize=10,
        )
        fig.tight_layout(rect=[0, 0.06, 1, 0.94])
        destination = (
            Path(__file__).resolve().parents[1]
            / "docs/images/lung-research-workflow.png"
        )
        fig.savefig(destination, dpi=160, facecolor=fig.get_facecolor())
        plt.close(fig)
        print(destination)


if __name__ == "__main__":
    main()
