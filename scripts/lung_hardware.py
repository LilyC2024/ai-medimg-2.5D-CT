"""Report actual hardware; never infer present devices from historical benchmarks."""

import argparse
import importlib.metadata
import json
import platform
from pathlib import Path


def inspect_hardware():
    import torch

    result = {
        "schema": "lung-hardware-v1",
        "os": platform.platform(),
        "processor": platform.processor(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": [
            torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
        ],
        "openvino_devices": [],
        "training_backend": "CUDA required by lung training launcher; NPU is inference-only",
        "historical_npu_result": "reports/intel_benchmark.json is old tissue-model evidence, not lung-detector acceleration",
    }
    try:
        import openvino as ov

        result["openvino"] = importlib.metadata.version("openvino")
        result["openvino_devices"] = ov.Core().available_devices
    except ImportError:
        result["openvino"] = "not installed"
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output")
    a = p.parse_args()
    result = inspect_hardware()
    if a.output:
        Path(a.output).parent.mkdir(parents=True, exist_ok=True)
        Path(a.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
