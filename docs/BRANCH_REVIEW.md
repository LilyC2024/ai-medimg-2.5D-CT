# Reviewed branch integration — 24 October 2026

Every fetched remote branch and local non-main branch was compared against the
previous main. Changes were selectively integrated and repaired, rather than
blindly merging entire tips. The original branches remain available. Branch
commit messages and claimed test counts were not accepted as validation evidence.

| Reviewed branch | Tip | Decision |
| --- | --- | --- |
| `origin/ci/hardening` | `8229eaea54b9` | Adapted lint/type/coverage, audits, SBOM, secret scanning and CodeQL. Run results recorded separately; CI configuration alone is not a passed check. |
| `origin/docs/data-terms` | `22e4b0e8bab3` | Integrated MIT source license/data terms; datasets, weights and third-party code retain separate terms. |
| `origin/docs/honest-process-wording` | `18b68a01275e` | Adapted qualification of AI-assisted source review; preserved actual coding-agent review history. No independent clinician/security certification claimed. |
| `origin/feat/signed-exchange` | `eb0acc37561e` | Adapted coordinated Ed25519 exchange, strict bounded archive/envelope validation, pinned-key receiver policy and accurately labelled producer declarations. |
| `origin/repair/reproducible-ct` | `c075888bad37` | Superseded/previous release; no historical code restored. |

## Cross-project result

The original schema versions and unsigned fictional/public-research examples stay
compatible. Optional signatures identify an exporter and bind exact manifest and
artifact bytes. A pinned key is a local trust decision, not clinical validation;
unknown signed keys are rejected by LOVISA. Producer-declared unmatched-candidate
fractions are exploratory precision proxies, not specificity or cancer risk.

The shared attestation module is identical in all three repositories. It bounds
ZIP sizes before decompression, rejects duplicate/unsafe members and JSON keys,
reconstructs artifact hashes, validates strict claims and verifies Ed25519 proofs.
Code source licensing is MIT; data/model terms remain separate.

## Validation and limitations

See [EVALUATION.md](../EVALUATION.md) for checks actually executed on the integrated
source. Offline tests use generated data/scripted reviews; live model smokes are
identified separately. Existing trained models are reused; no new clinical
validation, GPU training, NPU execution or clinician qualification is claimed.
