"""Actual local inference smoke on generated CT; never approves a report or measures clinical accuracy."""
import argparse
import json
from pathlib import Path
import tempfile
import time

from lung_nodule.detection import MonaiDetector, PhantomDetector, detect_study
from lung_nodule.phantom import generate_chest
from lung_nodule.workspace import load_workspace, reviewed_report, save_workspace


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-dir",help="Use real pretrained weights; omit for explicitly labeled fixture finder")
    p.add_argument("--device",choices=["cpu","cuda"],default="cpu")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    import torch
    torch.set_num_threads(4)
    started=time.perf_counter()
    detector=MonaiDetector(a.model_dir,device=a.device) if a.model_dir else PhantomDetector()
    if not a.model_dir and a.device!="cpu":
        p.error("Fixture finder is CPU-only; use --model-dir for accelerator smoke")
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        study,hu=detect_study(generate_chest(root/"ct"),detector,study_id="smoke",patient_alias="synthetic")
        save_workspace(root/"workspace",study,hu)
        load_workspace(root/"workspace")
        try:
            reviewed_report(root/"workspace")
        except FileNotFoundError:
            blocked=True
        else:
            raise AssertionError("Unreviewed report unexpectedly available")
    result={"schema":"lung-local-smoke-v1","input":"generated 32x64x64 chest-like phantom; not clinical evaluation",
            "detector":study.model.model_dump(mode="json"),"candidate_count":len(study.candidates),
            "report_without_review_blocked":blocked,"review_approval_issued":False,
            "elapsed_seconds":time.perf_counter()-started}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
