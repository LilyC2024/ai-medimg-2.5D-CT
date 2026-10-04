from __future__ import annotations
import numpy as np
from robustness import LabelPostprocessConfig, postprocess_multiclass_prediction


def apply_day6_postprocess(
    probabilities_bchw: np.ndarray,
    *,
    brain_min_voxels: int = 256,
    bone_min_voxels: int = 96,
    overlap_min_voxels: int = 32,
    smooth_iterations: int = 1,
) -> np.ndarray:
    predicted_labels = probabilities_bchw.argmax(axis=1).astype(np.uint8)
    return postprocess_multiclass_prediction(
        probabilities=np.transpose(probabilities_bchw, (1, 0, 2, 3)),
        predicted_labels=predicted_labels,
        class_configs={
            1: LabelPostprocessConfig(
                min_component_size=int(brain_min_voxels),
                fill_holes=True,
                smooth_iterations=int(smooth_iterations),
                keep_largest_component=True,
            ),
            2: LabelPostprocessConfig(
                min_component_size=int(bone_min_voxels),
                fill_holes=False,
                smooth_iterations=int(smooth_iterations),
                keep_largest_component=True,
            ),
            3: LabelPostprocessConfig(
                min_component_size=int(overlap_min_voxels),
                fill_holes=True,
                smooth_iterations=int(smooth_iterations),
                keep_largest_component=False,
            ),
        },
    ).astype(np.uint8, copy=False)
