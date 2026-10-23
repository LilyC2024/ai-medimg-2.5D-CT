# MHCRA lung integration

[Overview](../../README.md) · [Companion setup/use](https://github.com/LilyC2024/Medical-AI/blob/main/docs/IMAGING.md)

## Implemented compatibility

CT v0.10 and MHCRA v0.2 exchange **mhcra-lung-nodules-v2**: generated synthetic
source HU, every-slice source/box previews, candidates, model/source provenance,
optional producer review and canonical evidence-linked report. MHCRA validates the
full bundle independently, provides candidate/caliper controls and requires its own
**authenticated imaging acceptance**. Its final seven-section clinical report
requires another explicit approval. Upstream local CT attestation cannot bypass
these MHCRA gates.

| Contract/capability | Status |
| --- | --- |
| Current nodule-v2 | Implemented producer, receiver, viewer, measurements and research appendix |
| Legacy mhcra-imaging-v1 | Original tissue-mask producer/receiver retained |
| Old mhcra-lung-nodules-v1 | Incomplete; rejected with instruction to re-export original workspace |
| Public research DICOM, full CT, training/evaluation | Standalone CT only; no import into synthetic MHCRA |

No medical hypotheses are added from images. Images/reviewer notes never enter
Ollama; clinical safety escalation cannot be lowered. Accepted/rejected candidates
and reviewer-selected distances are research annotations, not clinical diagnoses.

## Launch through MHCRA

Install this repository in its own Python 3.12 `.venv` with matching CPU or CUDA
torch/torchvision and `.[ml,lung,ui,dev]`. Keep MHCRA's separate existing environment.
MHCRA finds a sibling checkout or uses `MHCRA_CT_ROOT`. Its UI offers the non-ML
fixture, installed pretrained detector with explicit device, and legacy demo.
Installed pretrained weights can be configured with `MHCRA_CT_MODEL_DIR`.
No downloads during inference and no unavailable-device fallback.

The MHCRA-specific bridge exports **pending review** rather than forging the
standalone reviewer step:

```bash
.venv/bin/python -m deploy.mhcra_lung_bridge --patient-id synthetic-checklist --study-id synthetic-example --output-dir artifacts/mhcra-lung --mode fixture --device cpu
# Real pretrained detector, with explicitly downloaded/verified local weights:
.venv/bin/python -m deploy.mhcra_lung_bridge --patient-id synthetic-checklist --study-id synthetic-pretrained --output-dir artifacts/mhcra-pretrained --mode pretrained --model-dir models/luna16 --device cpu
```

Output is `<output-dir>/exchange/bundle.mhcra.zip`. The generated study's patient
alias/study ID match the MHCRA request. Use new immutable IDs/directories per run.
The bridge never supplies human approval. The default standalone CLI `export`
still requires its explicit reviewed workspace; its optional producer review is
preserved in v2, while MHCRA always demands its own separate authenticated review.
For manual export set `patient_alias` equal to the selected MHCRA synthetic ID.

## Contract details and bounds

`bundle.json` binds identity, unknown acquisition date, processing time, typed
Study, pending/reviewed status and artifact sizes/SHA-256. `source.npy` holds finite
float32 HU; all slice source/overlay PNGs and `producer/report.md` are listed.
Pending report text is fixed; reviewed report is regenerated from Study/Review.
No arbitrary ungrounded report prose can enter the receiver.

MHCRA limits: 64 source slices, 256×256 plane, 64MiB ZIP, 128MiB expanded, 131
members and 400KB manifest. Validate NPY headers/length before allocation, reject
unsafe/duplicate/unlisted/encrypted entries, verify every hash and recompute every
PNG pixel. Box and caliper rasterization uses NumPy without font dependencies.
The full HU snapshot enables the receiver to calculate and display new calipers.
Standalone public-research and full-volume workspaces retain their own larger
bounds; export does not truncate them to fit MHCRA.

`contracts.py` and `exchange_contract.py` are ML-free. MHCRA vendors them as
`nodule_models.py` and `nodule_exchange.py`, changing only the import path. Its
`scripts/sync_ct_contracts.py` checks equality; integration CI pins the tested CT
commit. Change producer first, test, intentionally sync the consumer, test it,
then run real joint smokes before updating the pin. Hashes prove consistency,
not independent synthetic origin, execution authenticity or clinical truth.

## Agents and models

The CT package has no autonomous LLM agents. MONAI 3D RetinaNet is a CV detector;
geometry, measurements, review and report are Python. MHCRA separately runs
history, medication, reasoning and safety components in LangGraph. Only reasoning
calls local Ollama. The CT worker is not a fifth LLM agent and supplies no model
tools. [Function reference](code-reference.md) · [Evaluation](../../EVALUATION.md).
