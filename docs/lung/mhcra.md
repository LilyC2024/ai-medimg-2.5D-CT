# MHCRA integration boundary

[Overview](../../README.md) · [Existing companion](https://github.com/LilyC2024/Medical-AI)

## Current compatibility

MHCRA currently accepts `mhcra-imaging-v1`: generated-synthetic four-class tissue
mask bundles. Its producer is retained unchanged in deploy/mhcra_bridge.py with its
tests. Existing MHCRA jobs can continue calling that interface. Its old limits and
class meanings are intentional; lung boxes must not be mislabeled as those masks.

The new lung workflow exports `mhcra-lung-nodules-v1`, with study, review, report and
candidate PNG previews. Only generated synthetic studies can be exported. This
is a versioned research exchange, **not an implemented MHCRA consumer**. The current
MHCRA importer must reject it. Public research patient images/records cannot enter
MHCRA's synthetic database through either path.

## Deliberate next consumer extension

1. Add a separate bounded nodule-aware importer, with patient/study identity,
   source/model/recipe hashes, geometry, every candidate and reviewed caliper.
2. Validate preview and measurement consistency and preserve original exchange
   separately from clinical-record facts. Uploaded producer declarations cannot
   independently prove model execution or real-world truth.
3. Present candidates as model-generated research observations, retaining accepted,
   rejected and uncertain state. MHCRA imaging acceptance must be authenticated and
   distinct from a final clinical-report approval.
4. Keep existing deterministic urgent/uncertain safety routing before reasoning.
   Imaging must never lower escalation or silently expand the hypothesis catalog.
5. Add approved research summaries as a separate evidence-linked appendix. Any
   future imaging hypotheses require an explicit tested catalog/schema extension.

No MHCRA code or safety policy was changed by this CT-focused release.

## Agents and models

The CT package has **no autonomous LLM agents**. The image detector is a neural
computer-vision model; the geometry, measurements, review and report are Python.
MHCRA separately coordinates its history, medication, clinical reasoning and
safety roles with LangGraph. Only its reasoning role calls local Ollama; the other
three roles use deterministic Python. Images do not reach that LLM through this
release. More LLM agents would not supply missing lesion labels or validation.
