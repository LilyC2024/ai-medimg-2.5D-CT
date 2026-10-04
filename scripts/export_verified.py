import argparse
import json
import time
from pathlib import Path
import sys
import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
from data.ct25d_dataset import CT25DDataset
from deploy.inference_runtime import (
    load_checkpoint,
    build_model_from_checkpoint,
    export_checkpoint_to_onnx,
    validate_onnx_equivalence,
)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--index", required=True)
    p.add_argument("--onnx", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    torch.set_num_threads(1)
    c = load_checkpoint(a.checkpoint)
    model = build_model_from_checkpoint(c)
    dataset = CT25DDataset(a.index, split="test")
    if not len(dataset):
        raise ValueError("Test split empty.")
    inputs = torch.stack([dataset[i]["image"] for i in range(len(dataset))])
    targets = torch.stack([dataset[i]["mask"] for i in range(len(dataset))])
    hw = (c["resize"]["height"], c["resize"]["width"])
    inputs = F.interpolate(inputs, size=hw, mode="bilinear", align_corners=False)
    targets = F.interpolate(targets[:, None].float(), size=hw, mode="nearest")[
        :, 0
    ].long()
    with torch.no_grad():
        logits = model(inputs)
        for _ in range(3):
            model(inputs[:1])
        latency = []
        for i in range(30):
            start = time.perf_counter()
            model(inputs[i % len(inputs) : i % len(inputs) + 1])
            latency.append(time.perf_counter() - start)
    export_checkpoint_to_onnx(a.checkpoint, a.onnx)
    evidence = validate_onnx_equivalence(a.checkpoint, a.onnx, inputs.numpy())
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out / "runtime_inputs.npz",
        inputs=inputs.numpy(),
        torch_logits=logits.numpy(),
        targets=targets.numpy(),
    )
    evidence.update(
        {
            "opset": 17,
            "exporter": "torch.onnx.export legacy TorchScript dynamo=False",
            "input_contract": ["dynamic CPU batch", 3, *hw],
            "torch_version": str(torch.__version__),
            "pytorch_cpu_p50_ms": float(np.percentile(latency, 50) * 1000),
            "pytorch_cpu_p95_ms": float(np.percentile(latency, 95) * 1000),
            "warmup": 3,
            "repeats": 30,
            "threads": 1,
        }
    )
    (out / "onnx_parity.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence))
    if not evidence["within_tolerance"]:
        raise SystemExit(1)
