"""Producer signatures: pinned verification, tamper rejection and honest performance."""

import io
import json
import os
import zipfile

import pytest
from pydantic import ValidationError

from deploy.mhcra_lung_bridge import generate_bundle
from lung_nodule.cli import main
from lung_nodule.exchange_contract import read_exchange
from lung_nodule.producer_signature import (
    NOT_MEASURED,
    SIGNATURE_ENTRY,
    Performance,
    check_archive,
    generate_key,
    load_private_key,
    sign_archive,
)
from lung_nodule.workspace import export_synthetic_exchange


@pytest.fixture
def key(tmp_path):
    path = tmp_path / "keys/ct.key"
    info = generate_key(path)
    trusted = {info["key_id"]: dict(info, producer="lovisa-ct", label="test CT")}
    return path, trusted


@pytest.fixture
def pending(tmp_path):
    generate_bundle(tmp_path / "job", "synthetic-checklist", "s1")
    return tmp_path / "job/workspace"


def entries(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {n: z.read(n) for n in z.namelist()}


def pack(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        for name, value in files.items():
            z.writestr(name, value)
    return out.getvalue()


def test_signed_export_verifies_against_pinned_key_and_reader_accepts_it(
    tmp_path, key, pending
):
    path, trusted = key
    out = export_synthetic_exchange(
        pending, tmp_path / "signed.zip", pending=True, signing_key=path
    )
    data = out.read_bytes()
    read_exchange(data, "synthetic-checklist")
    check = check_archive(data, trusted)
    assert check.status == "verified" and check.producer == "lovisa-ct"
    assert check.label == "test CT" and check.performance == NOT_MEASURED
    assert check_archive(data, {}).status == "untrusted-key"


def test_unsigned_export_is_reported_not_trusted(tmp_path, key, pending):
    data = export_synthetic_exchange(pending, tmp_path / "u.zip", pending=True)
    assert SIGNATURE_ENTRY not in entries(data.read_bytes())
    assert check_archive(data.read_bytes(), key[1]).status == "unsigned"


def test_tampered_bundle_claims_or_signature_fail_closed(tmp_path, key, pending):
    path, trusted = key
    data = export_synthetic_exchange(
        pending, tmp_path / "s.zip", pending=True, signing_key=path
    ).read_bytes()
    files = entries(data)
    manifest = json.loads(files["bundle.json"])
    manifest["job_id"] = "f" * 32
    with pytest.raises(ValueError, match="does not match this bundle"):
        check_archive(pack(dict(files, **{"bundle.json": json.dumps(manifest)})), trusted)
    envelope = json.loads(files[SIGNATURE_ENTRY])
    envelope["claims"]["performance"] = {
        "measured": True,
        "metric": "invented",
        "false_positive_fraction": 0.01,
        "test_images": 1000,
        "negative_images": 1000,
        "evaluation_sha256": "a" * 64,
        "limitations": "forged",
    }
    with pytest.raises(ValueError, match="verification failed"):
        check_archive(pack(dict(files, **{SIGNATURE_ENTRY: json.dumps(envelope)})), trusted)
    wrong = {k: dict(v, producer="lovisa-endo") for k, v in trusted.items()}
    with pytest.raises(ValueError, match="verification failed"):
        check_archive(data, wrong)
    with pytest.raises(ValueError, match="already signed"):
        sign_archive(data, load_private_key(path), "lovisa-ct")


def test_key_files_are_owner_only_and_never_overwritten(tmp_path, key):
    path, _ = key
    with pytest.raises(FileExistsError):
        generate_key(path)
    if os.name == "posix":
        assert path.stat().st_mode & 0o077 == 0
        path.chmod(0o644)
        with pytest.raises(ValueError, match="chmod 600"):
            load_private_key(path)


def test_performance_cannot_claim_a_rate_without_evidence():
    with pytest.raises(ValidationError):
        Performance(measured=True, metric="fp", limitations="none")
    with pytest.raises(ValidationError):
        Performance(
            measured=False,
            metric="fp",
            false_positive_fraction=0.5,
            limitations="none",
        )


def test_cli_keygen_prints_public_key_only(tmp_path, capsys):
    main(["keygen", "--output", str(tmp_path / "cli.key")])
    printed = json.loads(capsys.readouterr().out)
    assert set(printed) == {"producer", "key_id", "public_key_b64"}
    assert "PRIVATE" not in json.dumps(printed)
