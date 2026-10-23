"""Explicit setup-only TCIA public download for the fixed LIDC-IDRI-0002 demo.

Local inference never calls this script. Download permission is not clinical review.
TCIA deidentified dates are retained in original files, never interpreted as real dates.
"""

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://services.cancerimagingarchive.net/nbia-api/services/v1/"
SUBJECT = "LIDC-IDRI-0002"


def download(url, path, limit):
    """Stream a TLS-verified public file to a bounded exclusive temporary file."""
    temp = path.with_suffix(path.suffix + ".partial")
    total = 0
    try:
        with urllib.request.urlopen(url, timeout=60) as source, temp.open("xb") as out:
            while chunk := source.read(1024**2):
                total += len(chunk)
                if total > limit:
                    raise ValueError("Public download exceeds size limit")
                out.write(chunk)
        temp.rename(path)
    finally:
        temp.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--accept-public-data-terms", action="store_true")
    a = p.parse_args()
    if not a.accept_public_data_terms:
        raise ValueError(
            "Read TCIA LIDC-IDRI CC BY 3.0 terms and explicitly accept public-research use"
        )
    root = a.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    query = urllib.parse.urlencode(
        dict(Collection="LIDC-IDRI", PatientID=SUBJECT, Modality="CT")
    )
    with urllib.request.urlopen(BASE + "getSeries?" + query, timeout=40) as r:
        rows = json.loads(r.read(1024**2))
    if (
        len(rows) != 1
        or rows[0]["PatientID"] != SUBJECT
        or "3.0" not in rows[0]["LicenseName"]
    ):
        raise ValueError("Unexpected public dataset metadata/license")
    m = rows[0]
    (root / "metadata.json").write_text(json.dumps(m, indent=2))
    archive = root / "series.zip"
    download(
        BASE
        + "getImage?"
        + urllib.parse.urlencode(dict(SeriesInstanceUID=m["SeriesInstanceUID"])),
        archive,
        160 * 1024**2,
    )
    series = root / "series"
    series.mkdir()
    with zipfile.ZipFile(archive) as z:
        items = z.infolist()
        if len(items) > 600 or sum(i.file_size for i in items) > 300 * 1024**2:
            raise ValueError("Public series archive exceeds bounds")
        names = set()
        for i in items:
            if i.is_dir():
                continue
            name = Path(i.filename).name
            if name in names:
                raise ValueError("Duplicate archive basename")
            names.add(name)
            # Do not extract archive paths or any unneeded executable/metadata files.
            if name.lower().endswith(".dcm"):
                (series / name).write_bytes(z.read(i))
            elif name == "LICENSE":
                (root / name).write_bytes(z.read(i))
    xml = root / "LIDC-XML-only.zip"
    download(
        "https://www.cancerimagingarchive.net/wp-content/uploads/LIDC-XML-only.zip",
        xml,
        20 * 1024**2,
    )
    with zipfile.ZipFile(xml) as z:
        if sum(i.file_size for i in z.infolist()) > 200 * 1024**2:
            raise ValueError("XML archive too large")
        found = 0
        for i in z.infolist():
            if i.filename.endswith(".xml"):
                data = z.read(i)
                if (
                    m["SeriesInstanceUID"].encode() in data
                    and b"<LidcReadMessage" in data
                ):
                    (root / "annotations.xml").write_bytes(data)
                    found += 1
        if found != 1:
            raise ValueError("Expected exactly one CT annotation document")
    (root / "approval.json").write_text(
        json.dumps(
            dict(
                public_research_only=True,
                dataset="TCIA LIDC-IDRI-0002",
                license="CC BY 3.0",
                approved_by="explicit-public-research-setup",
                protocol="public-chest-protocol-unverified",
            ),
            indent=2,
        )
    )
    (root / "download-sha256.json").write_text(
        json.dumps(
            {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (archive, xml)
            },
            indent=2,
        )
    )
    print(
        "Public research data ready:",
        root,
        "; protocol remains unverified; no clinician approval recorded.",
    )


if __name__ == "__main__":
    main()
