"""Full model OpenVINO CPU/NPU comparison on identical held-out tensors.
Requires openvino, numpy, onnxruntime; no torch dependency in the Intel environment.
"""

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path
import importlib.metadata as metadata
import numpy as np
import onnxruntime as ort
import openvino as ov


def softmax(x):
    e = np.exp(x - x.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)


def scores(pred, target):
    dice = {}
    for i in range(1, 4):
        a, b = pred == i, target == i
        n = int(a.sum() + b.sum())
        dice[str(i)] = float(2 * np.logical_and(a, b).sum() / n) if n else None
    values = [v for v in dice.values() if v is not None]
    return {"dice": float(np.mean(values)) if values else 0.0, "per_class_dice": dice}


def peak_memory():
    if platform.system() != "Windows":
        return None
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t)
            for name in (
                "PeakWorkingSetSize",
                "WorkingSetSize",
                "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage",
                "PagefileUsage",
                "PeakPagefileUsage",
            )
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    ctypes.windll.psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        return int(counters.PeakWorkingSetSize)
    return None


def benchmark(model_path, input_path, output, runs=30):
    d = np.load(input_path)
    inputs = d["inputs"]
    reference = d["torch_logits"]
    targets = d["targets"]
    core = ov.Core()
    report = {
        "schema_version": 1,
        "model_sha256": hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        "input_shape": list(inputs.shape),
        "split": "test",
        "metric_grid": "256x256 model grid, nearest resized teacher labels",
        "sample_count": len(inputs),
        "warmup": 3,
        "repeats": runs,
        "versions": {
            p: metadata.version(p) for p in ("openvino", "onnxruntime", "numpy")
        },
        "os": platform.platform(),
        "thresholds": {
            "cpu_atol": 1e-4,
            "cpu_rtol": 1e-3,
            "cpu_mask_agreement": 0.999,
            "npu_absolute_dice_drop": 0.01,
        },
        "settings": {
            "threads": 1,
            "requests": 1,
            "cache": "disabled",
            "power_mode": "Balanced (powercfg)",
            "plugged_in": "unknown: Win32_Battery returned no instance",
        },
        "pytorch_cpu": scores(reference.argmax(1), targets),
        "runtimes": {},
    }
    runtimes = []
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    start = time.perf_counter()
    session = ort.InferenceSession(
        str(model_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    runtimes.append(
        (
            "onnxruntime_cpu",
            lambda x: session.run(None, {"input": x})[0],
            time.perf_counter() - start,
            ["CPUExecutionProvider"],
            "FP32",
        )
    )
    for device in ("CPU", "NPU"):
        try:
            model = core.read_model(str(model_path))
            model.reshape({model.input(0): [1, 3, 256, 256]})
            settings = {"PERFORMANCE_HINT": "LATENCY"}
            if device == "CPU":
                settings.update(
                    {"INFERENCE_PRECISION_HINT": "f32", "INFERENCE_NUM_THREADS": 1}
                )
            start = time.perf_counter()
            compiled = core.compile_model(model, device, settings)
            compile_seconds = time.perf_counter() - start
            raw_devices = compiled.get_property("EXECUTION_DEVICES")
            devices = (
                [raw_devices] if isinstance(raw_devices, str) else list(raw_devices)
            )
            try:
                precision = str(compiled.get_property("INFERENCE_PRECISION_HINT"))
            except Exception:
                precision = "not exposed"
            request = compiled.create_infer_request()
            runtimes.append(
                (
                    "openvino_" + device.lower(),
                    lambda x, r=request: np.array(r.infer({0: x})[0], copy=True),
                    compile_seconds,
                    devices,
                    precision,
                )
            )
        except Exception as e:
            report["runtimes"]["openvino_" + device.lower()] = {
                "status": "failed",
                "error_type": type(e).__name__,
                "error": str(e)[:3000],
            }
    for name, run, compile_seconds, devices, precision in runtimes:
        start = time.perf_counter()
        run(inputs[:1])
        first = time.perf_counter() - start
        for _ in range(3):
            run(inputs[:1])
        latencies = []
        for i in range(runs):
            start = time.perf_counter()
            run(inputs[i % len(inputs) : i % len(inputs) + 1])
            latencies.append(time.perf_counter() - start)
        logits = np.concatenate([run(x[None]) for x in inputs])
        prob = softmax(logits)
        refprob = softmax(reference)
        metrics = scores(logits.argmax(1), targets)
        drop = report["pytorch_cpu"]["dice"] - metrics["dice"]
        agreement = float(np.mean(logits.argmax(1) == reference.argmax(1)))
        report["runtimes"][name] = {
            "status": "executed",
            "execution_devices": devices,
            "precision_hint": precision,
            "compile_seconds": compile_seconds,
            "first_inference_seconds": first,
            "p50_ms": float(np.percentile(latencies, 50) * 1000),
            "p95_ms": float(np.percentile(latencies, 95) * 1000),
            "throughput_stacks_s": float(1 / np.mean(latencies)),
            "metrics": metrics,
            "absolute_dice_drop": drop,
            "max_probability_difference": float(np.abs(prob - refprob).max()),
            "mean_probability_difference": float(np.abs(prob - refprob).mean()),
            "max_logit_difference": float(np.abs(logits - reference).max()),
            "mask_agreement": agreement,
            "cpu_gate": bool(
                np.allclose(prob, refprob, atol=1e-4, rtol=1e-3) and agreement >= 0.999
            ),
            "npu_dice_gate": bool(drop <= 0.01),
            "observed_peak_process_memory_bytes": peak_memory(),
        }
    report["passed"] = (
        all(
            report["runtimes"].get(name, {}).get("cpu_gate", False)
            for name in ("onnxruntime_cpu", "openvino_cpu")
        )
        and report["runtimes"].get("openvino_npu", {}).get("npu_dice_gate", False)
        and report["runtimes"].get("openvino_npu", {}).get("execution_devices")
        == ["NPU"]
    )
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", required=True)
    p.add_argument("--inputs", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--runs", type=int, default=30)
    a = p.parse_args()
    result = benchmark(a.onnx, a.inputs, a.output, a.runs)
    raise SystemExit(0 if result["passed"] else 1)
