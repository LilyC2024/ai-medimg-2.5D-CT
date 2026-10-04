# Architecture and contracts

Input is one regular CT DICOM series. Output is a source-grid uint8 label mask with class IDs 0–3 plus numeric geometry. Users are engineers and research reviewers. Clinical users and diagnostic use are outside the current intended purpose.

## Data flow

DICOM stored pixels → one modality rescale → physical-coordinate resampling → head ROI crop → HU clipping [-1000,1000] and normalization [0,1] → ordered three-slice stacks → U-Net logits → optional volume postprocessing → inverse resize/crop/resampling → source-grid mask.

Slices sort by ImagePositionPatient projected onto the normal computed from ImageOrientationPatient. Direction columns are the DICOM x direction, y direction and cross-product normal in LPS. Array order is z,y,x. Origin, direction and spacing are preserved in transform metadata and exported NPZ/NIfTI. Resampling maps physical voxel centers with scale target_spacing/source_spacing; output size is round((source_size-1)*source_spacing/target_spacing)+1. Crop bounds are inclusive at minima and exclusive at maxima. Crop origin is source origin plus direction times the physical crop offset. Inverse label interpolation is nearest neighbor. Cropped-out source pixels are background. Landmark and oblique-grid regression tests verify these mappings.

Coarse 5 mm z spacing is retained because interpolating additional slices does not create anatomical information. In-plane resampling changes sampling, not source resolution. Forward/inverse index scales and crop origins are recorded in the manifest. Model resize is bilinear for intensities with align_corners=False; training labels resize by nearest neighbor. Deployment restores probabilities to the crop grid, assigns class IDs, and restores labels to the source grid.

## Four pseudo classes

Class 0 is neither candidate; class 1 is brain-like candidate excluding the broad bone candidate; class 2 is broad bone candidate excluding the brain-like candidate; class 3 is their overlap. The current teacher's bone threshold is **-100 HU**, followed by opening/closing, component-size filtering and largest-component selection. This includes soft tissue and must not be described as a validated skull mask. The brain-like candidate uses an adaptive sweep around a window centered at 40 HU, width 120, normalized interval [0.05,0.95], head gate -10 HU, component/morphology/continuity heuristics and a separate high-HU exclusion candidate. The complete parameter set is versioned in each manifest; adaptive selected parameters are recorded too. Class assignment is brain→1, bone→2, overlap→3. These are heuristic targets, not anatomical ground truth.

Local review across processed z=0,5,10,15,20,25,29 found no labels on crop extremes, extensive overlap in central tissue, and a broad peripheral class-2 region including nonbone tissue. Class 1 is tiny (870 voxels in the full processed case). Threshold quality flags alone would not reveal these limitations. No expert quality approval is inferred.

## 2.5D and network

Channels are [max(z-1,0),z,min(z+1,depth-1)] and the target is the center slice. Boundary channels repeat the boundary slice. The native crop is resized to 256 x 256 in the baseline. A compact PyTorch U-Net uses base width 16, encoder widths 16/32/64, bottleneck 128, and three transposed-convolution decoder stages with concatenated skips. Each block has two bias-free 3x3 convolutions, BatchNorm and ReLU; pooling is 2x2. A 1x1 head produces four logits. Parameter count: **482,788**. MONAI has no implemented role and was removed from dependencies.

Adam, deterministic seed 13, eight epochs, batch size 2 and LR 0.001 are recorded in `configs/baseline.json`. The loss is half class-weighted cross entropy and half foreground soft Dice. Augmentation uses synchronized flips/rotations and image-only intensity jitter. Seed includes sample identity and epoch, giving reproducible variation across epochs. Validation foreground macro Dice selects the checkpoint. Primary baseline temperature is 1; fitting calibration on model-selection data is omitted. A guarded exploratory fitter falls back to identity if NLL worsens or optimization fails.

## Splits and metrics

The single-case contiguous demonstration reserves two center slices at each boundary for radius 1. Retained centers differ by at least three; pairwise support sets, including clamped boundaries, are disjoint. For multiple series, all known series from a patient must share a split; the loader rejects cross-series patient leakage. A single-series split is explicitly a software demonstration, not unseen-subject evaluation.

Evaluation requires an explicit nonempty split, sorts by series/slice, processes a single series per invocation, and applies morphology after concatenating predictions into contiguous runs. Gaps are never treated as adjacent slices. Global voxel counts determine per-class Dice/IoU and the unweighted foreground macro mean. Classes empty in both prediction and target have null metrics and are excluded; if all foreground classes are absent the summary is 0. False positives in an absent target class score 0. Teacher-versus-itself agreement is tautological and cannot establish model superiority. Test data is reserved from parameter selection.

## Runtime

ONNX opset 17 exports fixed 3 x H x W spatial dimensions with dynamic CPU batch size to preserve the existing CLI contract. NPU compilation specializes to fixed [1,3,256,256]. The legacy TorchScript exporter is deliberately selected and its deprecation is recorded; graph checking and measured parity are mandatory. CPU gate: probabilities atol=1e-4/rtol=1e-3 and mask agreement >=99.9%. Near ties can change argmax despite close probabilities; they are reported. FP16 NPU quality uses a predeclared absolute Dice-drop investigation threshold <=0.01, not a clinical safety gate. CPU ONNX sessions and API checkpoint/session initialization are reused. GPU comparisons are optional and separate.

Support isolation measures direct neighboring-slice tensors after a common deterministic transform; ROI crop decisions and the classical teacher use the whole series. This further limits the intra-series demonstration and is not an independent-patient training protocol. A future patient-level split must be defined before processing each subject independently.
