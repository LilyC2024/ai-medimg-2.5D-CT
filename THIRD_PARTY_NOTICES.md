# Third-party research components

The repository's original code is MIT except adaptations retaining upstream terms.
The topology/preprocessing in `lung_nodule/detection.py` follows the
[MONAI lung_nodule_ct_detection bundle](https://github.com/Project-MONAI/model-zoo/tree/dev/models/lung_nodule_ct_detection).

Copyright (c) MONAI Consortium. Licensed under the Apache License, Version 2.0.
The [Apache-2.0 text](third_party/MONAI-APACHE-2.0.txt) is retained locally.
The recipe adapts source-array loading, explicit devices and physical box
restoration. No original authorship of the detector architecture, pretrained
weights or upstream trainer is claimed.

Explicit `fetch-model` setup retains official LICENSE/data-license files beside
the downloaded assets. Weights/config/scripts are not committed. MONAI, PyTorch,
torchvision, Streamlit and other dependencies retain their own terms; datasets
have separate access/attribution requirements. Code licensing grants no patient-
data, weight or clinical-use permission.

LOVISA vendors the ML-free contract/renderer under this repository's MIT notice;
its own project-wide licensing status is documented separately in its repository.
