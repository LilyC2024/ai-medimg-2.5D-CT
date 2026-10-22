import numpy as np
import pytest

from lung_nodule.contracts import Geometry
from lung_nodule.detection import PhantomDetector, detect_study, map_boxes, prepare_tensor, select_device
from lung_nodule.phantom import generate_chest


def test_fixture_detection_and_negative_study(tmp_path):
    for lesion, expected in ((True, 1), (False, 0)):
        series = generate_chest(tmp_path / str(lesion), lesion=lesion)
        study, _ = detect_study(series, PhantomDetector(), study_id="demo", patient_alias="synthetic")
        assert len(study.candidates) == expected and study.model.synthetic_fixture
        if lesion:
            np.testing.assert_allclose(study.candidates[0].box_zyx, (14, 26, 18, 18, 34, 26))


def test_ras_lps_boxes_source_mapping_includes_all_corners():
    g = Geometry(shape_zyx=(20, 30, 40), spacing_zyx_mm=(2, 1, 1),
                 origin_lps_mm=(10, 20, 30), direction_lps=(1, 0, 0, 0, 1, 0, 0, 0, 1))
    affine = np.array([[-1,0,0,-10], [0,-1,0,-20], [0,0,2,30], [0,0,0,1]])
    out = map_boxes([[3,4,5,8,9,10]], [.8], affine, g, .1)
    np.testing.assert_allclose(out[0].box_zyx, [5,4,3,10,9,8])
    with pytest.raises(ValueError):
        map_boxes([[1,2,3,4,5,6]], [float("nan")], affine, g, .1)


def test_prepare_tensor_physical_roundtrip(tmp_path):
    pytest.importorskip("monai")
    series = generate_chest(tmp_path / "ct")
    study, hu = detect_study(series, PhantomDetector(), study_id="s", patient_alias="p")
    image = prepare_tensor(hu, study.geometry)
    assert image.shape[0] == 1 and 0 <= image.min() <= image.max() <= 1
    ras = image.affine.numpy()
    assert np.allclose(np.linalg.norm(ras[:3,:3], axis=0), [.703125,.703125,1.25])
    # Known source physical location maps back independently of RAS reorientation.
    point = study.geometry.to_lps([16,30,22])
    index = np.linalg.solve(ras[:3,:3], point * [-1,-1,1] - ras[:3,3])
    box = np.r_[index-1, index+1]
    candidate = map_boxes([box], [.9], ras, study.geometry, .1)[0]
    np.testing.assert_allclose((np.array(candidate.box_zyx[:3])+candidate.box_zyx[3:])/2, [16,30,22], atol=1e-5)


def test_requested_accelerator_never_silently_falls_back(monkeypatch):
    import torch
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    for device in ("cuda", "npu", "auto"):
        with pytest.raises(ValueError, match="unavailable or unsupported"):
            select_device(device)


def test_actual_random_weight_network_and_sliding_window_forward():
    pytest.importorskip("monai")
    pytest.importorskip("torchvision")
    import torch
    from lung_nodule.detection import build_detector
    previous=torch.get_num_threads()
    try:
        torch.set_num_threads(2)
        detector=build_detector("cpu",score_threshold=.99).eval()
        detector.set_sliding_window_inferer(roi_size=[32,32,16],overlap=.25,sw_batch_size=1,mode="constant",device="cpu")
        with torch.inference_mode():
            out=detector([torch.zeros(1,32,32,16)],use_inferer=True)[0]
        assert out["box"].shape[1]==6 and torch.isfinite(out["label_scores"]).all()
    finally:
        torch.set_num_threads(previous)
