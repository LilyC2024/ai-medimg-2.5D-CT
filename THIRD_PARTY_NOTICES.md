# Third-party research components

Original repository code is MIT, except adaptations that retain upstream terms.
The 3D RetinaNet topology/preprocessing recipe in lung_nodule/detection.py follows
the MONAI Consortium's Apache-2.0 lung_nodule_ct_detection model bundle:
https://github.com/Project-MONAI/model-zoo/tree/dev/models/lung_nodule_ct_detection

Copyright (c) MONAI Consortium. Licensed under the Apache License, Version 2.0:
https://www.apache.org/licenses/LICENSE-2.0
The recipe was adapted for local source-array input, explicit devices and physical
box restoration. No claim of original authorship of the detector architecture,
pretrained weights or upstream training implementation is made.

The explicit model fetch retains official LICENSE and data-license files beside
the downloaded weights/config/scripts. Those downloads are not committed here.
MONAI, PyTorch, torchvision, Streamlit and other dependencies retain their own
licenses. Research datasets have separate access/attribution conditions. MIT code
licensing does not grant patient-data, weight or clinical-use permission.
