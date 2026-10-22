"""Full local detection latency on unchanged inputs; no clinical or NPU claims."""
import argparse
import json
from pathlib import Path
import time

import numpy as np

from lung_nodule.detection import MonaiDetector, detect_study
from lung_nodule.contracts import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--series",required=True)
    p.add_argument("--model-dir",required=True)
    p.add_argument("--device",choices=["cpu","cuda"],required=True)
    p.add_argument("--approval")
    p.add_argument("--runs",type=int,default=5)
    p.add_argument("--threads",type=int,default=4)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    if a.runs<2 or a.threads<1: p.error("At least two runs and one thread required")
    import torch
    torch.set_num_threads(a.threads)
    start=time.perf_counter()
    model=MonaiDetector(a.model_dir,device=a.device)
    setup=time.perf_counter()-start
    def run():
        study,_=detect_study(a.series,model,study_id="benchmark",patient_alias="research",approval=a.approval)
        if a.device=="cuda": torch.cuda.synchronize()
        return study
    t=time.perf_counter();first=run();cold=time.perf_counter()-t
    times=[]
    for _ in range(a.runs):
        t=time.perf_counter(); study=run();times.append(time.perf_counter()-t)
        if study.source_sha256!=first.source_sha256: raise ValueError("Benchmark source changed")
    result={"schema":"lung-full-volume-latency-v1","model":first.model.model_dump(mode="json"),
        "source_sha256":first.source_sha256,"shape_zyx":first.geometry.shape_zyx,"input_kind":first.input_kind,
        "model_load_seconds":setup,"first_run_seconds":cold,"warmup_runs":1,"runs":a.runs,"threads":a.threads,
        "p50_seconds":float(np.percentile(times,50)),"p95_seconds":float(np.percentile(times,95)),
        "candidate_snapshot_sha256":digest([c.model_dump(mode="json") for c in first.candidates]),
        "scope":"DICOM IO, hashing, preprocessing, inference and source mapping; no review/export; no diagnostic accuracy metric"}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=="__main__":main()
