# Cleanup inventory

| Paths | Reason and replacement | Verification |
| --- | --- | --- |
| data_processed/index.csv | Untrack stale absolute paths/UIDs; generated relative manifests replace it | New case generation, reference/checksum tests and relocated-root run |
| saved_models/best.pt | Historical sole checkpoint retained locally, untracked; corrected artifacts ignored | weights_only=True safe load and exact architecture match, 482788 parameters |
| outputs/* | Historical images/reports kept locally; no redistribution permission inferred | New sanitized reports and local QA exist; Git history preserves old evidence |
| docs/day4_data_module.md, day5_unet_cpu.md, day7_deploy.md | Competing old contracts consolidated | architecture.md and reproducibility.md cover implementation and commands |
| docs/interview_notes.md, one_page_summary.md | Remove coaching and repeated claims after migration | Scope/tradeoffs/failures covered in README and model_card.md |
| docs/limitation_improvements.md, project_journal.md, release_notes_v1.0.md | Unsupported calibration/leakage/release claims superseded | Git commit 457ddbf retains chronology; release_notes.md identifies repaired results |
| scripts/preprocess_series.py, classical_baseline.py, make_index.py | Consolidate duplicate preprocessing/data paths into thin compatibility wrappers | prepare_case.py generates images, labels, frozen split and contract together |
| requirements.txt | Forward to authoritative pyproject rather than duplicate dependencies | Clean editable installation |
| MONAI | No implemented usage | Removed dependency, imports/tests pass |
| Production sys.path changes | Installed modules and explicit deploy packaging replace them | CLI test runs from a different cwd |
| Missing-artifact skip tests | Generated CT/checkpoint/ONNX replace private fixtures | Required synthetic tests execute; no all-skip success |
| .vscode, .venv, egg-info, caches, artifacts | Local files ignored; no machine settings published | Staged-path and public-metadata inspection |
| src/.gitkeep | Obsolete placeholder | Real source files present |

No source CT, sole historical checkpoint or local backup evidence was deleted. Ordinary cleanup does not rewrite Git history or erase previously committed identifiers. The src/ct25d destination is deferred: packaging of the tested existing modules is functional, and a namespace rewrite is not necessary for the correctness repairs.
