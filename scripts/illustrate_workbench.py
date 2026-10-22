"""Plot source/overlay previews from a generated-synthetic MHCRA bundle."""
import argparse
import io
import json
from pathlib import Path
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, FuncFormatter
import numpy as np
from PIL import Image


def illustrate(bundle, output):
    with zipfile.ZipFile(bundle) as archive:
        manifest = json.loads(archive.read("bundle.json"))
        if manifest.get("synthetic") is not True or manifest.get("schema_version") != "mhcra-imaging-v1":
            raise ValueError("A generated-synthetic workbench bundle is required")
        depth = manifest["geometry"]["shape_zyx"][0]
        slices = [depth // 4, depth // 2, min(depth - 1, 3 * depth // 4)]
        fig = plt.figure(figsize=(14, 8), facecolor="#f6f9fc")
        grid = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1.25], wspace=.14, hspace=.18)
        for row, role in enumerate(("source_preview", "overlay_preview")):
            for col, index in enumerate(slices):
                item = next(a for a in manifest["artifacts"] if a["role"] == role and a["slice_index"] == index)
                image = np.asarray(Image.open(io.BytesIO(archive.read(item["path"]))))
                ax = fig.add_subplot(grid[row, col])
                ax.imshow(image, interpolation="nearest")
                ax.set_title(f"{'Synthetic source' if row == 0 else 'Unvalidated overlay'} · slice {index}", fontsize=11, color="#102443")
                ax.axis("off")
        counts = manifest["voxel_counts"]
        colors = ["#63768b", "#00b4aa", "#f5a523", "#a55ad2"]
        ax = fig.add_subplot(grid[0, 3])
        ax.barh([f"Class {i}" for i in range(4)], counts, color=colors)
        ax.set_title("Candidate voxels · source grid", fontsize=11, color="#102443")
        ax.set_xlabel("Voxel count", fontsize=10)
        ax.xaxis.set_major_locator(MaxNLocator(3))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, position: f"{value / 1000:g}k"))
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)
        details = fig.add_subplot(grid[1, 3])
        details.axis("off")
        shape = " × ".join(map(str, manifest["geometry"]["shape_zyx"]))
        spacing = " × ".join(f"{v:g}" for v in manifest["geometry"]["spacing_zyx_mm"])
        details.text(0, .98, f"LOCAL CT → MHCRA\n\nSource grid: {shape} (z,y,x)\nSpacing: {spacing} mm\nAcquisition date: unavailable\nRaw predictions · producer reports\nONNX parity passed\n\nSynthetic research model\nHeuristic labels; quality unvalidated\nNo anatomy or lesion diagnosis\n\nInspect → accept research appendix\n→ separate final report approval", va="top", fontsize=10, linespacing=1.4, color="#102443")
        fig.suptitle("MHCRA + CT: inspect the source, then review the model output", fontsize=19, fontweight="bold", color="#102443", y=.97)
        fig.legend(handles=[Patch(color=colors[i], label=label) for i, label in enumerate([
            "0: neither candidate", "1: brain-like only", "2: broad bone candidate", "3: overlap"])],
            loc="lower center", bbox_to_anchor=(.5, .085), ncol=4, frameon=False, fontsize=10)
        fig.text(.5, .055, "Generated synthetic pixels only · candidate classes are unvalidated · class 0 and cropped-out regions do not establish normality", ha="center", fontsize=10, color="#31465f")
        fig.text(.5, .028, "Source/overlay previews and counts come from the same hash-bound bundle; this figure demonstrates software integration, not clinical accuracy.", ha="center", fontsize=9, color="#31465f")
        fig.subplots_adjust(top=.87, bottom=.19, left=.035, right=.97)
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=160, facecolor=fig.get_facecolor())
        plt.close(fig)
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(illustrate(args.bundle, args.output))
