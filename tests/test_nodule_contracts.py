import json

import numpy as np
import pytest
from pydantic import ValidationError

from lung_nodule.contracts import Caliper, Candidate, Geometry
from lung_nodule.phantom import generate_chest
from lung_nodule.sources import load_sources


def test_source_identity_order_geometry_and_tamper(tmp_path):
    series = generate_chest(tmp_path / "series")
    hu, geometry, sources, identity, kind, _ = load_sources(series)
    assert hu.shape == (32, 64, 64) and kind == "generated-synthetic"
    assert len(sources) == len({s.sop_uid_sha256 for s in sources}) == 32
    assert sources[0].index == 0 and len(identity) == 64
    assert geometry.spacing_zyx_mm == (1.5, 1.0, 1.0)
    path = next(series.iterdir())
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="marker mismatch"):
        load_sources(series)


def test_geometry_oblique_roundtrip_and_physical_caliper():
    g = Geometry(
        shape_zyx=(20, 40, 60),
        spacing_zyx_mm=(2.0, 3.0, 4.0),
        origin_lps_mm=(10.0, 20.0, 30.0),
        direction_lps=(1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0),
    )
    points = np.array([[1.0, 2.0, 3.0], [7.0, 11.0, 13.0]])
    np.testing.assert_allclose(g.from_lps(g.to_lps(points)), points)
    assert Caliper(start_zyx=(2, 3, 4), end_zyx=(2, 6, 8)).length_mm(
        g
    ) == pytest.approx(np.sqrt(9**2 + 16**2))
    with pytest.raises(ValueError):
        Caliper(start_zyx=(1, 2, 3), end_zyx=(2, 2, 3)).length_mm(g)


@pytest.mark.parametrize(
    "box", [(1, 2, 3, 1, 4, 5), (1, 2, 3, 4, 1, 5), (1, 2, 3, 4, 5, float("nan"))]
)
def test_invalid_boxes(box):
    with pytest.raises(ValidationError):
        Candidate(candidate_id="n1", box_zyx=box, score=0.5)


def test_real_data_requires_separate_explicit_approval(tmp_path):
    series = generate_chest(tmp_path / "series")
    series.with_name("series.synthetic.json").unlink()
    with pytest.raises(ValueError, match="approval"):
        load_sources(series)
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "public_research_only": True,
                "dataset": "fixture",
                "license": "fixture",
                "approved_by": "test",
                "protocol": "adult-noncontrast-chest-complete",
            }
        )
    )
    assert load_sources(series, approval=approval)[4] == "approved-public-research"


def test_one_coarse_inplane_axis_rejected_for_research(tmp_path):
    import pydicom

    series = generate_chest(tmp_path / "series")
    series.with_name("series.synthetic.json").unlink()
    for path in series.iterdir():
        ds = pydicom.dcmread(path)
        ds.PixelSpacing = [1.0, 2.0]
        ds.save_as(path, enforce_file_format=True)
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "public_research_only": True,
                "dataset": "fixture",
                "license": "fixture",
                "approved_by": "test",
                "protocol": "adult-noncontrast-chest-complete",
            }
        )
    )
    with pytest.raises(ValueError, match="resolution"):
        load_sources(series, approval=approval)


def test_source_allocation_limit_is_checked_before_decode(tmp_path):
    from dicom_loader import load_dicom_series

    series = generate_chest(tmp_path / "ct")
    with pytest.raises(ValueError, match="dimensions"):
        load_dicom_series(series, max_voxels=100)
    with pytest.raises(ValueError, match="allocation"):
        load_dicom_series(series, max_voxels=1024**3)
