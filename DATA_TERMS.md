# Dataset and model terms

The [MIT license](LICENSE) covers this repository's original source code only.
Adapted upstream code keeps its notice ([third-party](THIRD_PARTY_NOTICES.md)).
The code license grants no rights to datasets, scans, annotations, weights or
patient data, and no permission for clinical use. Research only; not a
diagnostic device.

No dataset pixels, annotations or weights belong in Git. Anyone who downloads them
must accept and follow the publisher's current terms themselves:

| Source | Used for | Terms as documented here (check the publisher before use) |
| --- | --- | --- |
| [TCIA LIDC-IDRI](https://www.cancerimagingarchive.net/collection/lidc-idri/) | Research localization smoke (subject LIDC-IDRI-0002) and LOVISA composite demo | CC BY 3.0 and the TCIA data usage policy; credit the collection and its dataset DOI |
| [MONAI lung_nodule_ct_detection bundle](https://github.com/Project-MONAI/model-zoo/tree/dev/models/lung_nodule_ct_detection) | Pretrained RetinaNet weights downloaded by `fetch-model` | Upstream license files are kept beside the weights; trained on LUNA16, which is derived from LIDC-IDRI, so overlap with LIDC-IDRI evaluation is possible |
| Historical legacy sample (`dicom_series_01`) | Early 2.5D experiments | Source, terms and redistribution permission were never supplied; it must not be redistributed ([legacy data](docs/data.md)) |

Generated synthetic fixtures are MIT licensed with the code.
