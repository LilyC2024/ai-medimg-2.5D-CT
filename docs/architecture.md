# Legacy 2.5D architecture

[Current lung architecture](lung/architecture.md) · [Legacy overview](legacy-pipeline.md)

This guide describes the retained tissue-mask experiment, not the nodule detector.

## Data and geometry

Order slices by projected physical position. Apply modality rescale once; exclude
stored padding from statistics. Resample physical voxel centers, record direction/
origin/spacing and crop bounds, then clip HU [−1000,1000] to normalize [0,1].
Resize intensities bilinearly and labels with nearest neighbor. Inverse restoration
returns labels to source geometry; cropped-out pixels become background.

Coarse 5 mm slice spacing is retained because interpolation adds no source detail.
The teacher uses whole-series head/morphology heuristics. Its −100 HU broad-bone
threshold includes soft tissue; brain-like/overlap classes are not expert anatomy.

## Network and evaluation

Channels are previous/current/next slices; boundary channels repeat. A compact
U-Net has base width 16 and 482,788 parameters for the recorded 256×256 baseline.
CE/foreground-Dice loss and validation-selected training use the frozen baseline
configuration. Training augmentation varies reproducibly with epoch/sample.

Same-series demonstration splits discard two centers at each boundary so retained
radius-one stacks have disjoint support. Whole-series preprocessing still limits
independence; this is not patient-level validation. Evaluation requires an explicit
nonempty split, sorts slices and postprocesses contiguous runs only. Global counts
produce class Dice/IoU; both-empty classes are null/excluded. Primary temperature
is identity; historical calibration failures remain recorded.

## Deployment contracts

ONNX opset 17 has fixed spatial dimensions and dynamic CPU batch. NPU compilation
specializes `[1,3,256,256]`. CPU gates use atol 1e-4/rtol 1e-3 probability agreement
and ≥99.9% mask agreement. FP16 NPU uses a separate absolute Dice-drop investigation
threshold ≤0.01. These are engineering gates, not clinical acceptance criteria.

Deployment binds graph, checkpoint and preprocessing hashes. Unsupported geometry,
changed artifacts or parity failures stop execution. [Reproduce](reproducibility.md)
· [Evidence](validation.md).
