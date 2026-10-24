# Public CT excerpt for the LOVISA research demo

[CT overview](../../README.md) · [Integration](mhcra.md) · [Training](training.md)

Use deidentified **TCIA LIDC-IDRI-0002**, CC BY 3.0. Source/terms:
[TCIA LIDC-IDRI](https://www.cancerimagingarchive.net/collection/lidc-idri/).
The commands use the setup directory `models/luna16`; substitute an existing
verified directory such as `models/luna16-full` when reusing local assets.
This fixed scan has unconfirmed contrast status. Missing tags are not evidence
of noncontrast acquisition. The public research path records protocol uncertainty;
it makes no clinical validation claim. Deidentified dates remain unknown in exports.

```bash
.venv/bin/python scripts/fetch_lidc_demo.py --output /absolute/path/LIDC-IDRI-0002 --accept-public-data-terms
.venv/bin/python -m lung_nodule.cli detect --series /absolute/path/LIDC-IDRI-0002/series --approval /absolute/path/LIDC-IDRI-0002/approval.json --model-dir models/luna16 --device cpu --threads 4 --patient-alias LIDC-IDRI-0002 --study-id lidc0002-real --output artifacts/lidc0002-excerpt32-real --inference-region 168 313 300 32 96 96
.venv/bin/python scripts/evaluate_public_lidc.py --workspace artifacts/lidc0002-excerpt32-real --xml /absolute/path/LIDC-IDRI-0002/annotations.xml --output reports/lidc0002-localization.json
```

The evaluation uses per-reader >=3-mm contour observations, exact source SOP
mapping and a predicted-center/reader-box localization proxy with 2-mm margin.
It is not official LUNA scoring, consensus, pathology or independent validation;
pretrained overlap is possible. Annotations are never input to the detector.

Full-scan CPU inference is offline preparation and may take many minutes. Model
training is still the separate CUDA workflow, which was not executed on this host.
There is no hidden CPU fallback for the full trainer.

For the LOVISA bundle, provide a provenance JSON with dataset, HTTPS source URL,
license, research_subject_id, the original workspace source.npy SHA-256 and
composite_case:true. `export-research` additionally takes `--patient-id`,
`--crop-origin Z Y X` and `--shape Z Y X`. It creates a pending, unreviewed,
source-mapped excerpt (at most 64×256×256), not an entire examination. Whole-study
metadata and original source hashes are preserved; the consumer independently
checks the excerpt pixels and mapping, not absent whole-scan bytes.

The [LOVISA research-kit script](https://github.com/LilyC2024/Medical-AI/blob/main/docs/RESEARCH_IMAGES.md)
automates a declared 32×96×96 ROI selected from a public reader annotation before model inference and adds
three fixed Kvasir test images from unrelated/unknown subjects. Their fictional
Jordan case never implies one real patient or a shared disease. Images, datasets,
weights and local reports remain excluded from Git. Exact research-v3 schemas
stay separate from legacy synthetic-v2; no public source is relabelled artificial.

Research CT additionally binds `inference_region_zyx` (origin Z/Y/X then depth/height/width). The consumer rejects crops/predictions outside the declared analysed region. No claim of full-scan inference is inferred from full-source metadata.

## Read the demonstration correctly

The public reader annotation selected the declared ROI before model inference.
That selection is part of the experiment and cannot be presented as an uninformed
whole-scan detection result. The export records analysed-region bounds separately
from full-source geometry. Newly strengthened workspace/source checks preserve
this evidence; the code review does not create a new clinical or independent
accuracy result. LOVISA now opens the ZIP using **Upload → Analyze**.
