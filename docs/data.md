# Data and public metadata

No real image data is distributed in the repository. The local 34-slice series has 512 x 512 pixels and spacing z/y/x = 5 / 0.488281 / 0.488281 mm. Its source URL, acquisition terms, ownership, and permitted redistribution have not been supplied. Do not assert a dataset license or offer a download for it. A reviewer must provide a permitted CT series, or run the synthetic fixture.

## Acquisition contract

Obtain authorization from the data owner, document the source URL and acquisition date locally, and confirm research/derived-artifact permissions. Place one single-frame CT series in a directory with only its DICOM files. Expected input is one monochrome CT series with ImagePositionPatient, ImageOrientationPatient, PixelSpacing, rescale slope/intercept and consistent dimensions. Supported regular oblique geometry is accepted; mixed series, localizers, multi-frame CT, duplicate/nonuniform positions, missing required tags and gantry-tilt/in-plane shifts fail clearly. At most 512 slices, 1024 pixels per dimension and 64 Mi voxels are supported. pydicom handles installed codecs; SimpleITK/GDCM provides an explicitly rescale-aware compressed fallback. Optional independent JPEG decoding: `pip install -e ".[codecs]"`.

```powershell
.\.venv\Scripts\python.exe scripts/prepare_case.py --series-dir data/dicom_series_01 --output-dir artifacts/real/processed
```

Missing data produces an actionable error. Output includes `volume.npz`, `labels.npz`, `index.csv`, its checksum, `manifest.json`, and technical metadata. All are local. Manifest file references are relative to its directory, or a caller-supplied data root, and are checked before training. Source-file ordinal/checksum manifests are local until permission to publish them is established. Checksums prove file identity, not anonymization.

## Publication allowlist

`src/public_metadata.py` admits only the reviewed numeric technical fields in `metadata/examples/sample_001.json`: schema version and case alias, modality, dimensions, spacing, orientation, origin, direction, projected positions, rescale ranges, padding count, nonpadding HU range and empty validation messages. Unknown fields and machine paths fail validation. Public data/split manifests use aliases and relative file references. Public evidence contains model/split hashes, software versions, configuration and metrics.

Patient IDs, dates, institutions, private tags and original UIDs are excluded. Originals remain local; changing aliases does not constitute full DICOM anonymization. No raw header dump is public. Technical metadata and identifier mappings are separate. Previously committed identifiers remain in Git history; ordinary cleanup does not erase them. A separate disclosure/history review is needed if their sensitivity warrants remediation.

Real overlays were reviewed locally for teacher failure modes; no image is authorized for redistribution. Burned-in text, faces and metadata require separate disclosure and rights review before any image publication. No human expert annotation or clinical quality approval is claimed. Synthetic images are generated from equations without copied headers or patient pixels.

HU investigation: stored padding -2000 with slope 1 and intercept -1024 corresponds to -3024 HU. SimpleITK already applies rescale; the old compressed path could add the intercept again, producing -4048. Corrected nonpadding range is -1024 to 2170 HU. Padding is excluded from intensity statistics and replaced with -1000 for ROI/preprocessing. See `reports/hu_investigation.json` for the evidence and independent-decoder availability.
