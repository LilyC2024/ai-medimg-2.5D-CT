# Changelog

Notable changes to the lung CT companion. Dated test outcomes live in
[EVALUATION.md](EVALUATION.md); older release records are in
[docs/lung/release.md](docs/lung/release.md) and
[docs/release_notes.md](docs/release_notes.md). Research software, not a
diagnostic device.

## Unreleased

### Added
- Ed25519 producer signatures for review ZIPs: `lung-nodule keygen`,
  `--signing-key`/`LOVISA_SIGNING_KEY_FILE` on `export`, `export-research` and the
  LOVISA bridge. The signed claims declare CT false-positive performance as not
  measured. New dependency: `cryptography`.

### Changed
- The shared nodule reader accepts one optional `signature.json` entry (limit
  131 → 132 members). Unsigned archives remain valid.

## 0.10.0 — 24 October 2026

Baseline before this changelog.
