import io
import json
import zipfile

import numpy as np
import pytest

from deploy.mhcra_lung_bridge import generate_bundle
from lung_nodule.contracts import Review, Decision, digest, Caliper
from lung_nodule.exchange_contract import read_exchange, byte_digest
from lung_nodule.workspace import (
    load_workspace,
    complete_review,
    export_synthetic_exchange,
)


def rewrite(data, mutate):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        files = {n: z.read(n) for n in z.namelist()}
    manifest = json.loads(files.pop("bundle.json"))
    mutate(manifest, files)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("bundle.json", json.dumps(manifest))
        for name, value in files.items():
            z.writestr(name, value)
    return out.getvalue()


def test_pending_producer_requires_human_and_exports_complete_source_grid(tmp_path):
    path = generate_bundle(tmp_path / "job", "synthetic-checklist", "s1")
    bundle, _, files = read_exchange(path.read_bytes(), "synthetic-checklist")
    assert bundle.status == "pending_review" and bundle.producer_review is None
    assert len(bundle.artifacts) == 66 and len(files) == 66
    assert not (tmp_path / "job/workspace/review.json").exists()
    assert (tmp_path / "job/series").is_dir()


def test_reviewed_export_recomposes_report_and_checked_caliper(tmp_path):
    generate_bundle(tmp_path / "job", "synthetic-checklist", "s1")
    workspace = tmp_path / "job/workspace"
    study, _ = load_workspace(workspace)
    review = Review(
        study_digest=digest(study),
        reviewer="Scripted synthetic reviewer",
        qualified_reviewer_attestation=True,
        approved=True,
        decisions=[
            Decision(
                candidate_id="N001",
                decision="accept",
                caliper=Caliper(start_zyx=(16, 30, 18), end_zyx=(16, 30, 26)),
            )
        ],
    )
    complete_review(workspace, review)
    archive = export_synthetic_exchange(workspace, tmp_path / "reviewed.zip")
    bundle, _, files = read_exchange(archive.read_bytes(), "synthetic-checklist")
    assert bundle.status == "producer_reviewed" and bundle.producer_review == review
    assert b"8.00 mm" in files["producer/report.md"]


@pytest.mark.parametrize(
    "issue",
    [
        "patient",
        "public",
        "identity",
        "status",
        "hash",
        "overlay",
        "report",
        "npysize",
        "geometry",
        "uncertain",
        "unlisted",
    ],
)
def test_invalid_nodule_exchanges_fail_closed(tmp_path, issue):
    archive = generate_bundle(
        tmp_path / "job", "synthetic-checklist", "s1"
    ).read_bytes()

    def mutate(m, f):
        if issue == "patient":
            m["patient_id"] = "other"
        if issue == "public":
            m["synthetic"] = False
        if issue == "identity":
            m["study"]["patient_alias"] = "other"
        if issue == "status":
            m["status"] = "producer_reviewed"
        if issue == "hash":
            f["source.npy"] = b"changed"
        if issue == "overlay":
            item = next(a for a in m["artifacts"] if a["role"] == "overlay_preview")
            from PIL import Image

            pixels = np.full((64, 64, 3), 77, dtype=np.uint8)
            out = io.BytesIO()
            Image.fromarray(pixels).save(out, format="PNG")
            f[item["path"]] = out.getvalue()
            item.update(
                sha256=byte_digest(out.getvalue()), size_bytes=len(out.getvalue())
            )
        if issue == "report":
            a = next(a for a in m["artifacts"] if a["role"] == "producer_report")
            f[a["path"]] = b"Cancer confirmed"
            a.update(sha256=byte_digest(f[a["path"]]), size_bytes=len(f[a["path"]]))
        if issue == "npysize":
            out = io.BytesIO()
            np.lib.format.write_array_header_1_0(
                out, {"descr": "<f4", "fortran_order": False, "shape": (10**9, 64, 64)}
            )
            f["source.npy"] = out.getvalue()
            a = next(a for a in m["artifacts"] if a["role"] == "source_volume")
            a.update(sha256=byte_digest(out.getvalue()), size_bytes=len(out.getvalue()))
        if issue == "geometry":
            m["study"]["geometry"]["spacing_zyx_mm"][0] = 0
        if issue == "uncertain":
            m["producer_review"] = {
                "approved": True,
                "qualified_reviewer_attestation": True,
                "reviewer": "test",
                "study_digest": digest(m["study"]),
                "decisions": [{"candidate_id": "N001", "decision": "uncertain"}],
            }
            m["status"] = "producer_reviewed"
        if issue == "unlisted":
            f["unlisted.txt"] = b"unlisted"

    with pytest.raises(ValueError):
        read_exchange(rewrite(archive, mutate), "synthetic-checklist")
