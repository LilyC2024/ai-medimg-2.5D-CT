# LOVISA integration

[CT overview](../../README.md) ·
[LOVISA setup/use](https://github.com/LilyC2024/Medical-AI/blob/main/docs/IMAGING.md)

**LOVISA — Medical History & Clinical Reasoning Assistant** is the history and
clinical-report application, formerly **MHCRA AI**. This CT project is its optional
image-analysis companion. This guide keeps its existing URL and `mhcra-*` interfaces
so existing links/integrations continue to work.

## See the two roles

![CT source, candidate and caliper](../images/lung-research-workflow.png)

CT takes source pixels to candidate boxes and human-selected distances. This
illustration uses generated pixels and a non-ML finder; it is not detector accuracy.
LOVISA takes history to a source-linked seven-section draft and final clinician
review. Its [original workflow and technical pictures](https://github.com/LilyC2024/Medical-AI/blob/main/docs/ILLUSTRATIONS.md)
explain its four specialists, local Ollama and approval gates; the pictures retain
the former MHCRA AI label.

| CT does | LOVISA does |
| --- | --- |
| Validate volume/source geometry and run local CV detection | Organize synthetic history and preserve source attribution |
| Display source, candidates and calipers | Independently inspect/accept a synthetic imaging bundle |
| Compose deterministic research summary | Reason over text only and add accepted imaging after reasoning |
| Require standalone review for normal export | Require authenticated imaging acceptance and separate final clinical approval |

No LLM reads CT pixels. Images/notes cannot lower LOVISA safety escalation or expand
its hypothesis catalog. CT is not a fifth LLM specialist.

## Compatibility

| Format/capability | Support |
| --- | --- |
| mhcra-lung-nodules-v2 | Implemented source HU, all-slice previews, candidates/calipers and research appendix |
| mhcra-imaging-v1 | Retained legacy tissue-mask path |
| incomplete mhcra-lung-nodules-v1 | Re-export original workspace; cannot migrate by renaming schema |
| Public-research/full-size CT, training and FROC | Standalone CT only; LOVISA accepts bounded generated-synthetic data |

## Prepare synthetic input

Install CT in its own Python 3.12 `.venv`; keep LOVISA's environment separate.
LOVISA discovers a sibling checkout or uses `MHCRA_CT_ROOT`; installed weights use
`MHCRA_CT_MODEL_DIR`. Its UI offers fixture, installed-pretrained CPU/CUDA and legacy
modes. Inference downloads nothing and never silently changes device.

```bash
# From CT: pending review, no human approval issued.
.venv/bin/python -m deploy.mhcra_lung_bridge --patient-id synthetic-checklist --study-id synthetic-example --output-dir artifacts/lovisa-lung --mode fixture --device cpu
# Actual installed pretrained detector, using a new study/output:
.venv/bin/python -m deploy.mhcra_lung_bridge --patient-id synthetic-checklist --study-id synthetic-pretrained --output-dir artifacts/lovisa-pretrained --mode pretrained --model-dir models/luna16 --device cpu
```

Output: `<output-dir>/exchange/bundle.mhcra.zip`. Patient alias/study ID match the
request. Use new immutable IDs/directories. The bridge produces **pending review**;
normal standalone `export` still requires completed CT review. Its optional producer
attestation can seed LOVISA controls but cannot approve LOVISA imaging/final output.
For manual export, set `patient_alias` to the selected LOVISA synthetic patient ID.

## What crosses the boundary

`bundle.json` contains identity, processing timestamp, unknown acquisition date,
typed Study/status/optional Review and artifact hashes/sizes. `source.npy` supplies
finite float32 HU; source/overlay PNGs cover every slice; `producer/report.md` is the
canonical reviewed report or fixed pending text.

LOVISA limits: **64 slices ×256×256**, 64 MiB ZIP, 128 MiB expanded, 131 members,
400 KB manifest. It checks NPY headers before allocation, validates safe paths and
hashes, and recomputes every preview/report. The shared NumPy renderer avoids font
version differences. Export rejects oversized studies rather than truncating them.

CT `contracts.py` and `exchange_contract.py` are ML-free. LOVISA vendors them as
`nodule_models.py` / `nodule_exchange.py` with one import rewrite. Its sync script
checks equality and CI pins a tested CT revision. Contract changes require producer,
consumer and joint tests. Hashes prove consistency, not independent origin/model
execution or clinical truth. [Function reference](code-reference.md).

## Responsive LOVISA workspace

In LOVISA, choose **CT review**. The local worker reports actual bridge stages
through fixed `LOVISA_STAGE=` lines and opens completed output for pending
inspection automatically. `generate_bundle(..., progress=None)` is backward
compatible; the optional callback receives `starting`, `model` (pretrained only),
`source`, `detect` and `export`. It supplies progress, never review approval.

LOVISA applies a 110-second process watchdog and exposes cancellation. Its viewer
checks the full accepted source once per view and each requested preview on
access; acceptance/final reports still fully revalidate. No schema, model,
training workflow or standalone CLI time limit changed.

Local generated 32×64×64 producer/receiver smokes took 1.65s (fixture) and 12.43s
(installed pretrained CPU). These individual runs do not establish diagnostic
accuracy, full-volume performance or GPU/NPU support. See the
[LOVISA response-budget guide](https://github.com/LilyC2024/Medical-AI/blob/main/docs/PERFORMANCE.md).
