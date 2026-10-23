"""One-series reader-level localization smoke against official LIDC XML contours.

Not LUNA scoring, reader consensus, pathology or independent clinical validation.
Annotations are used only after model inference and never to select predictions.
"""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from lung_nodule.sources import sha256
from lung_nodule.workspace import load_workspace


def annotation_boxes(xml_path, study):
    """Map included >=3-mm contour observations by exact hashed source SOP ID."""
    path = Path(xml_path)
    if path.stat().st_size > 8 * 1024**2:
        raise ValueError("Annotation file too large")
    raw = path.read_bytes()
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("XML declarations not supported")
    root = ET.fromstring(raw)
    for e in root.iter():
        e.tag = e.tag.rsplit("}", 1)[-1]
    if root.tag != "LidcReadMessage":
        raise ValueError("CT LIDC contours required; CXR annotations are different")
    indices = {s.sop_uid_sha256: s.index for s in study.sources}
    result = []
    for reader, session in enumerate(root.findall("readingSession"), 1):
        for nodule in session.findall("unblindedReadNodule"):
            # Small-nodule point annotations have no characteristic/contour data.
            if nodule.find("characteristics") is None:
                continue
            points = []
            for roi in nodule.findall("roi"):
                if roi.findtext("inclusion", "").upper() != "TRUE":
                    continue
                uid = roi.findtext("imageSOP_UID", "")
                z = indices.get(hashlib.sha256(uid.encode()).hexdigest())
                edges = roi.findall("edgeMap")
                if z is None:
                    raise ValueError("Annotation references a different source series")
                if len(edges) >= 3:
                    points.extend(
                        (z, float(e.findtext("yCoord")), float(e.findtext("xCoord")))
                        for e in edges
                    )
            if points:
                a = np.asarray(points)
                result.append(
                    dict(
                        reader=reader,
                        nodule_id=nodule.findtext("noduleID"),
                        box_zyx=[*a.min(0).tolist(), *a.max(0).tolist()],
                    )
                )
    if not result:
        raise ValueError("No source-matched CT contour observations")
    return result


def evaluate(workspace, xml):
    study, _ = load_workspace(workspace)
    truth = annotation_boxes(xml, study)
    all_count = len(truth)
    integrity = json.loads((Path(workspace) / "integrity.json").read_text())
    region = integrity.get("inference_region_zyx", [0, 0, 0, *study.geometry.shape_zyx])
    start, shape = np.array(region[:3]), np.array(region[3:])
    truth = [
        t
        for t in truth
        if np.all(np.array(t["box_zyx"][:3]) >= start)
        and np.all(np.array(t["box_zyx"][3:]) <= start + shape - 1)
    ]
    # A declared 2-mm expanded annotation box / predicted-center localization proxy.
    # Multiple readers can describe the same lesion: never pool as unique lesions.
    margin = 2 / np.asarray(study.geometry.spacing_zyx_mm)
    rows = []
    for reader in sorted({t["reader"] for t in truth}):
        observations = [t for t in truth if t["reader"] == reader]
        for t in observations:
            lo, hi = np.asarray(t["box_zyx"][:3]), np.asarray(t["box_zyx"][3:])
            matches = []
            for c in study.candidates:
                center = (np.asarray(c.box_zyx[:3]) + c.box_zyx[3:]) / 2
                if np.all(center >= lo - margin) and np.all(center <= hi + margin):
                    matches.append(c.candidate_id)
            rows.append(
                dict(
                    reader=reader,
                    annotation_id=t["nodule_id"],
                    matched_candidates=matches,
                )
            )
    return dict(
        schema_version="lidc-reader-localization-smoke-v1",
        study_sha256=sha256(Path(workspace) / "study.json"),
        xml_sha256=sha256(xml),
        candidate_count=len(study.candidates),
        reader_observations=len(truth),
        out_of_scope_reader_observations=all_count - len(truth),
        inference_region_zyx=region,
        roi_selection="Dataset-annotation-selected excerpt smoke, not detection accuracy"
        if "inference_region_zyx" in integrity
        else "Whole-source inference",
        matched_reader_observations=sum(bool(r["matched_candidates"]) for r in rows),
        criterion="predicted center within reader contour bounding box expanded by 2 mm",
        rows=rows,
        limitation="One research scan; possible LUNA pretrained overlap; no consensus, pathology, independent validation or specificity estimate.",
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", required=True)
    p.add_argument("--xml", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    report = evaluate(a.workspace, a.xml)
    Path(a.output).write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
