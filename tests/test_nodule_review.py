import json

import pytest

from lung_nodule.contracts import Caliper, Decision, Review, digest
from lung_nodule.detection import PhantomDetector, detect_study
from lung_nodule.phantom import generate_chest
from lung_nodule.workspace import (
    complete_review,
    export_synthetic_exchange,
    load_workspace,
    reviewed_report,
    save_workspace,
)


def make_workspace(tmp_path):
    study, hu = detect_study(
        generate_chest(tmp_path / "ct"),
        PhantomDetector(),
        study_id="s",
        patient_alias="synthetic",
    )
    path = save_workspace(tmp_path / "workspace", study, hu)
    return path, study


def approval(study, **overrides):
    values = dict(
        study_digest=digest(study),
        reviewer="Research reviewer",
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
    return Review(**(values | overrides))


def test_report_requires_review_source_evidence_and_physical_caliper(tmp_path):
    path, study = make_workspace(tmp_path)
    with pytest.raises(FileNotFoundError):
        reviewed_report(path)
    report = complete_review(path, approval(study))
    assert "8.00 mm" in report and "not lesion diameters" in report
    assert study.sources[16].sha256 in report and "no malignancy diagnosis" in report
    assert report == reviewed_report(path)
    assert export_synthetic_exchange(path, tmp_path / "research.zip").exists()


@pytest.mark.parametrize(
    "override",
    [
        {"approved": False},
        {"approved": "true"},
        {"qualified_reviewer_attestation": False},
        {"decisions": []},
        {"decisions": [Decision(candidate_id="N001", decision="uncertain")]},
        {
            "decisions": [
                Decision(
                    candidate_id="N001",
                    decision="reject",
                    caliper=Caliper(start_zyx=(16, 30, 18), end_zyx=(16, 30, 26)),
                )
            ]
        },
        {"study_digest": "0" * 64},
    ],
)
def test_invalid_or_stale_review_cannot_complete(tmp_path, override):
    path, study = make_workspace(tmp_path)
    with pytest.raises(ValueError):
        complete_review(path, approval(study, **override))
    assert not (path / "report.md").exists()


def test_tampered_snapshot_and_report_are_not_trusted(tmp_path):
    path, study = make_workspace(tmp_path)
    complete_review(path, approval(study))
    (path / "report.md").write_text("Cancer confirmed")
    assert "Cancer confirmed" not in reviewed_report(path)
    data = json.loads((path / "study.json").read_text())
    data["candidates"][0]["score"] = 0.9
    (path / "study.json").write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_workspace(path)


def test_ui_blocks_unattested_approval(tmp_path):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    path, _ = make_workspace(tmp_path)
    app = AppTest.from_file(
        str(Path(__file__).parents[1] / "src/lung_nodule/ui.py")
    ).run()
    app.text_input[0].set_value(str(path)).run()
    assert not app.exception
    next(b for b in app.button if b.label == "Complete research review").click().run()
    assert app.error and not (path / "review.json").exists()


def test_ui_accepted_candidate_and_attestation_produces_report(tmp_path):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    path, _ = make_workspace(tmp_path)
    app = AppTest.from_file(
        str(Path(__file__).parents[1] / "src/lung_nodule/ui.py")
    ).run()
    app.text_input[0].set_value(str(path)).run()
    next(s for s in app.selectbox if s.label == "Decision N001").set_value("accept")
    app.text_input[1].set_value("Scripted synthetic test reviewer")
    app.checkbox[-2].check()
    app.checkbox[-1].check()
    next(b for b in app.button if b.label == "Complete research review").click().run()
    assert not app.exception and (path / "review.json").exists()
    assert "no malignancy diagnosis" in reviewed_report(path)


def test_unicode_reviewer_and_report_use_utf8(tmp_path):
    path, study = make_workspace(tmp_path)
    review = approval(study, reviewer="研究者 Ω")
    complete_review(path, review)
    assert "研究者 Ω" in reviewed_report(path)
    assert "研究者 Ω" in (path / "review.json").read_bytes().decode("utf-8")


def test_docs_checker_ignores_platform_default_encoding(monkeypatch):
    from pathlib import Path
    from scripts.check_docs import main

    original = Path.read_text

    def windows_default(path, *args, **kwargs):
        kwargs.setdefault("encoding", "cp1252")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", windows_default)
    main()
