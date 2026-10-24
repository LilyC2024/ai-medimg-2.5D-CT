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
LOVISA creates one concise Clinical summary with history hypotheses, accepted CT
inspection, representative pictures and a brief clinician note. Detailed source
links stay in its evidence package; final clinician approval remains mandatory. Its [original workflow and technical pictures](https://github.com/LilyC2024/Medical-AI/blob/main/docs/ILLUSTRATIONS.md)
explain its four specialists, local Ollama and approval gates; the pictures retain
the former MHCRA AI label.

| CT does | LOVISA does |
| --- | --- |
| Validate volume/source geometry and run local CV detection | Organize synthetic history and preserve source attribution |
| Display source, candidates and calipers | Independently inspect/accept a synthetic or labelled public research bundle |
| Compose deterministic research summary | Reason over text only and add accepted imaging after reasoning |
| Require standalone review for normal export | Require authenticated imaging acceptance and separate final clinical approval |

No LLM reads CT pixels. Images/notes cannot lower LOVISA safety escalation or expand
its hypothesis catalog. CT is not a fifth LLM specialist.

## Compatibility

| Format/capability | Support |
| --- | --- |
| mhcra-lung-nodules-v2 | Implemented source HU, all-slice previews, candidates/calipers and combined report |
| mhcra-imaging-v1 | Retained legacy tissue-mask path |
| incomplete mhcra-lung-nodules-v1 | Re-export original workspace; cannot migrate by renaming schema |
| `lovisa-ct-research-v3` | Public source-mapped excerpt in a fictional composite case; declared dataset/license/subject provenance |
| Full-size CT, training and FROC | Standalone preparation; no full-volume coverage is implied by an excerpt |

## Prepare synthetic input

Install CT in its own Python 3.12 `.venv`; keep LOVISA's environment separate.
LOVISA discovers a sibling checkout or uses `MHCRA_CT_ROOT`; installed weights use
`MHCRA_CT_MODEL_DIR`; `MHCRA_CT_DEVICE` chooses `cpu` (default) or `cuda` for the
installed detector. The UI offers fixture, installed detector and legacy modes;
paths/device settings stay in local configuration. Inference downloads nothing and never silently changes device.

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
verifies accepted-study loading and the selected-view resolver, then checks each
requested preview on access instead of revalidating the archive per image.
Acceptance/final reports still fully revalidate. No schema, model,
training workflow or standalone CLI time limit changed.

Local generated 32×64×64 producer/receiver smokes took 1.65s (fixture) and 12.43s
(installed pretrained CPU). These individual runs do not establish diagnostic
accuracy, full-volume performance or GPU/NPU support. See the
[LOVISA response-budget guide](https://github.com/LilyC2024/Medical-AI/blob/main/docs/PERFORMANCE.md).

## Include inspection in the clinical report

In LOVISA, inspect the study and choose **Include reviewed CT in report** before
completing safety preparation. That preparation freezes the report's CT snapshot.
A study accepted later requires a new report; **Start a new report with CT** opens
that route for the same patient. Zero/rejected candidates do not establish a
normal CT, and missing calipers remain missing.

The Clinical summary includes candidate decisions and reviewed calipers, with
representative verified source/annotation pictures. A reviewer previews a brief
note before approving the changed text. The final HTML download embeds CT pictures
for offline use; Markdown contains the concise text, and JSON retains full original
citations, study provenance and decisions. At most three representative study
pictures/calipers are shown; all studies remain in the evidence package and viewer.
No CT image/measurement is interpreted by LOVISA's LLM.

[Current report guide and clearly labelled scripted example](https://github.com/LilyC2024/Medical-AI/blob/main/docs/REPORTS.md).
This updates documentation only; CT contracts, detector, measurements, training
and standalone research reports are unchanged.

## Public CT excerpt

Use `export-research`, not the synthetic bridge, for public studies. It leaves all
review pending and validates exact crop origin, physical geometry, source slices
and enclosed candidates against the original workspace. The report states
limited coverage and protocol uncertainty. [Reproducible real-image demo](public-demo.md).

## Current LOVISA actions and compatible repairs

In LOVISA select the matching case, **CT review → Upload → Analyze**. A ZIP opens
its included source/results without detector rerun. With no upload, Model/example
can launch an explicit generated fixture or installed-detector phantom. Resolve
all candidates and include the study before safety and final review. A valid new
image after preparation starts a fresh unreviewed context; old reports are intact.

The expert review changed numeric preflight/workspace and legacy upload handling,
not nodule-v2/research-v3/legacy-v1 schemas or renderer source. Exact vendored sync
and actual fixture/pretrained/legacy transfers remain required. Public research
provenance is an operator declaration, not independent source authentication.
[Source repairs](../review.md) · [Receiver workflow](https://github.com/LilyC2024/Medical-AI/blob/main/docs/WORKFLOWS.md).

## Optional signed export

Generate a new private key (never commit it):

```bash
.venv/bin/python -m lung_nodule.cli keygen --output /private/local-exporter.key
```

Pin the returned public key in LOVISA using
`python -m medical_assistant.producer_trust --producer lovisa-ct --public-key <public_key_b64> --label <name>`.
Keys require a trusted local identity check. Add `--signing-key /private/local-exporter.key`
to the companion export/infer command, or set `LOVISA_SIGNING_KEY_FILE`. A private
PEM must have owner-only POSIX permissions. No private key is sent to LOVISA.

The shared module bounds archives, rejects ambiguous paths/JSON and binds all
manifest-listed artifact hashes. Signed proof identifies the exporter, not clinical
accuracy. Unknown signed keys are blocked by LOVISA; unsigned older examples stay
compatible unless its trust settings require signatures. Existing schema versions
are retained. See [branch review](../BRANCH_REVIEW.md).
