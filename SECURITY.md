# CT security and research scope

Keep the standalone UI/API on loopback. It has no production authentication or
credential registry. Supported input is artificial pixels or explicitly permitted
deidentified research CT, not clinical records or real-patient linkage in LOVISA.
[Research scope](docs/regulatory_scope.md).

## Trust and evidence

Local operators, model installers, the filesystem and process administrator are
trusted. Hashes detect inconsistent artifacts, not a coordinated rewrite of all
local metadata, proof of anonymization, data permission or model execution.
Never load untrusted model graphs/checkpoints simply because they have hashes.
Exports can carry an Ed25519 producer signature (`keygen`, `--signing-key` or
`LOVISA_SIGNING_KEY_FILE`). Keep the private key owner-only (0600) and outside Git;
a signature identifies the key holder, not model correctness or data permission.
Pinned pretrained assets retain separate upstream terms; code publication grants
no dataset or model rights.

DICOM validation checks series identity, source ordering, geometry and allocation
bounds before processing. Research training verifies manifest paths/hashes,
patient separation, complete-label attestations, affine/spacing and finite real HU.
Source labels are validated before integer conversion; fractional/nonfinite/
complex class IDs cannot become valid targets by casting.

## Upload and workspace controls

The retained legacy API accepts a bounded ZIP containing one series. It rejects
unsafe paths, symlinks, encrypted or duplicate members, and oversized uploads.
The API owns its temporary extraction directory, so archive folder names cannot
change cleanup ownership. This API is a legacy segmentation path, not the lung
candidate service.

Lung workspaces preserve typed studies and float32 HU snapshots with hashes.
Invalid/nonrepresentable pixels fail before reserving an output directory.
Candidate decisions, optional calipers and report reconstruction must match the
same verified study. There is no automatic research approval. LOVISA applies
independent archive validation, authenticated image acceptance, safety and final
clinical approval; a producer review cannot substitute for those actions.

## Storage and publication

Source images, weights, local permission files, workspaces, logs and reviews are
not encrypted by this application and belong outside Git. Publish synthetic
reproductions, aggregate software evidence and source code only. Inspect history
as well as `.gitignore`; ignored files already committed remain published.

No cloud inference, paid API or remote tracing is required. Setup-only package/
model downloads are explicit. A candidate/measurement does not establish cancer,
normality, management recommendations or device certification. Report potential
vulnerabilities privately where a maintainer channel is available, using a small
artificial reproduction and no personal data.

[Expert repairs](docs/review.md) · [Validation](docs/validation.md).
