"""Manufactured HU/metadata only; not live research-model or clinician testing."""

import numpy as np
import pytest
from test_nodule_review import make_workspace

from lung_nodule.contracts import Study
from lung_nodule.exchange_contract import read_exchange
from lung_nodule.sources import sha256
from lung_nodule.workspace import (
    export_research_exchange,
    export_synthetic_exchange,
    save_workspace,
)


def test_public_export_preserves_crop_coordinates_and_stays_pending(tmp_path):
    old, fixture = make_workspace(tmp_path)
    from lung_nodule.workspace import load_workspace

    _, hu = load_workspace(old)
    data = fixture.model_dump()
    data.update(
        input_kind="approved-public-research",
        protocol_attestation="public-chest-protocol-unverified",
    )
    data["model"]["synthetic_fixture"] = False
    public = Study.model_validate(data)
    workspace = save_workspace(tmp_path / "public", public, hu)
    provenance = dict(
        dataset="scripted test",
        source_url="https://example.org/test",
        license="test-only",
        research_subject_id="unrelated-subject",
        original_sha256=sha256(workspace / "source.npy"),
        composite_case=True,
    )
    with pytest.raises(ValueError):
        export_synthetic_exchange(workspace, tmp_path / "old.zip", pending=True)
    dest = export_research_exchange(
        workspace,
        tmp_path / "public.zip",
        patient_id="research-composite-demo",
        research=provenance,
        crop_origin_zyx=(2, 5, 7),
        shape_zyx=(20, 50, 50),
    )
    b, _, _ = read_exchange(dest.read_bytes(), "research-composite-demo")
    assert (
        not b.synthetic and b.producer_review is None and b.status == "pending_review"
    )
    assert b.original_study == public
    assert np.allclose(
        b.study.geometry.to_lps((0, 0, 0)), public.geometry.to_lps((2, 5, 7))
    )
    assert b.study.geometry.shape_zyx == (20, 50, 50)
    with pytest.raises(ValueError):
        export_research_exchange(
            workspace,
            tmp_path / "bad.zip",
            patient_id="research-composite-demo",
            research=provenance,
            crop_origin_zyx=(1000, 0, 0),
            shape_zyx=(20, 50, 50),
        )


def test_explicit_excerpt_inference_maps_candidates_to_full_source(tmp_path):
    """Scripted detector checks crop geometry; this is not a live-model accuracy test."""
    from lung_nodule.contracts import Candidate
    from lung_nodule.detection import PhantomDetector, detect_study
    from lung_nodule.phantom import generate_chest

    class ScriptedDetector:
        provenance = PhantomDetector.provenance

        def predict(self, hu, geometry):
            assert hu.shape == (8, 20, 20)
            assert geometry.shape_zyx == hu.shape
            return [
                Candidate(candidate_id="N001", box_zyx=(1, 2, 3, 5, 10, 12), score=1.0)
            ]

    series = generate_chest(tmp_path / "roi-series")
    study, hu = detect_study(
        series,
        ScriptedDetector(),
        study_id="roi",
        patient_alias="synthetic",
        inference_region=(4, 10, 12, 8, 20, 20),
    )
    assert study.geometry.shape_zyx == hu.shape == (32, 64, 64)
    assert study.candidates[0].box_zyx == (5.0, 12.0, 15.0, 9.0, 20.0, 24.0)
    assert "excerpt only" in study.model.name
    assert study.model.config_sha256 != ScriptedDetector.provenance.config_sha256
