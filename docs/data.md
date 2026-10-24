# Legacy data and public metadata

[Current lung input rules](lung/data.md) · [Legacy pipeline](legacy-pipeline.md)

The earlier measured sample had 34 slices, 512×512 pixels and 5/.488281/.488281 mm
spacing. Its source URL, acquisition terms and redistribution permission were not
supplied. It is not distributed; exact public reproduction is unavailable.
Use generated fixtures or independently permitted data.

The shared loader requires one regular single-frame monochrome CT series with
physical position/orientation, spacing and rescale metadata. Mixed/localizer/
multiframe/irregular/shifted series fail. Regular oblique geometry is supported.
The legacy default bound is 512 slices, 1024 pixels per plane dimension and 64 Mi
voxels. pydicom handles installed codecs; the SimpleITK fallback is rescale-aware.
Optional JPEG codecs use `.[codecs]`.

`prepare_case.py` writes local volume/labels/index/checksum/manifest artifacts.
References are relative to the manifest or explicit data root. Original DICOM,
UID mapping, dates, patient/institution tags and machine paths stay private.
`public_metadata.py` publishes only reviewed numeric technical fields in the
[allowlisted example](../metadata/examples/sample_001.json).

Aliases/hashes are not complete anonymization. Review burned-in text, identifying
anatomy and rights before publishing images. Previously committed identifiers
remain in Git history unless separately remediated; ignoring a file does not erase
history. No original image redistribution is approved here.

The historical HU repair prevented double rescale in compressed fallback. Stored
padding −2000 with intercept −1024 corresponds to −3024 HU, not −4048; padding is
excluded/replaced for preprocessing. [Recorded investigation](../reports/hu_investigation.json).

## Numeric target and upload validation

Class labels must be real finite integer IDs in the supported range before any
cast. A fractional value is rejected rather than rounded/truncated. Archive
uploads accept one series only, reject encrypted/duplicate/unsafe members and
have explicit caller-owned cleanup. Dataset declarations and hashes remain
consistency evidence, not permission or anonymization. [Expert review](review.md).
