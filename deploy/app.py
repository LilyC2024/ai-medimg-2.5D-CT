"""Experimental localhost API. CLI is the primary validated interface."""

import io
import json
import os
import shutil
import tempfile
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response

ROOT = Path(__file__).resolve().parents[1]
from config import PreprocessConfig
from deploy.inference_runtime import (
    load_checkpoint,
    build_model_from_checkpoint,
    create_onnx_session,
    run_deployment_inference,
    unzip_series_bytes,
)


@asynccontextmanager
async def lifespan(app):
    app.state.ready = False
    app.state.checkpoint_path = Path(
        os.getenv("CT25D_CHECKPOINT", str(ROOT / "artifacts/real/models/best.pt"))
    )
    app.state.onnx_path = Path(
        os.getenv("CT25D_ONNX", str(ROOT / "artifacts/real/model.onnx"))
    )
    try:
        app.state.checkpoint = load_checkpoint(app.state.checkpoint_path)
        build_model_from_checkpoint(app.state.checkpoint)
        app.state.session = create_onnx_session(app.state.onnx_path)
        shape = app.state.session.get_inputs()[0].shape
        if shape[1:] != [
            3,
            app.state.checkpoint["resize"]["height"],
            app.state.checkpoint["resize"]["width"],
        ]:
            raise ValueError("Runtime shape mismatch")
        app.state.ready = True
    except Exception:
        pass  # Readiness exposes unavailable runtime without leaking paths or DICOM headers.
    yield


app = FastAPI(title="CT25D experimental API", version="0.8.0", lifespan=lifespan)


@app.get("/health")
def health():
    if not getattr(app.state, "ready", False):
        raise HTTPException(503, "Model runtime unavailable")
    return {"status": "ready", "runtime": "ONNX Runtime CPU"}


@app.post("/predict")
def predict(dicom_zip: UploadFile = File(...)):
    if not getattr(app.state, "ready", False):
        raise HTTPException(503, "Model runtime unavailable")
    payload = dicom_zip.file.read(64 * 1024 * 1024 + 1)
    if len(payload) > 64 * 1024 * 1024:
        raise HTTPException(413, "Upload exceeds 64 MiB")
    extracted = None
    try:
        extracted = unzip_series_bytes(payload)
        cleanup = extracted
        while not cleanup.name.startswith("ct25d_dicom_"):
            cleanup = cleanup.parent
        with tempfile.TemporaryDirectory(prefix="ct25d_result_") as tmp:
            result = run_deployment_inference(
                series_dir=extracted,
                checkpoint_path=app.state.checkpoint_path,
                onnx_path=app.state.onnx_path,
                output_dir=tmp,
                preprocess_config=PreprocessConfig(),
                save_overlays=False,
                validate_onnx=False,
                runtime_checkpoint=app.state.checkpoint,
                runtime_session=app.state.session,
            )
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(result.output_paths.mask_volume_path, "prediction_mask.npz")
                z.write(result.output_paths.preprocess_report_path, "technical.json")
            return Response(
                archive.getvalue(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=prediction.zip"},
            )
    except (
        ValueError,
        FileNotFoundError,
        zipfile.BadZipFile,
        __import__("pydicom").errors.InvalidDicomError,
    ):
        raise HTTPException(422, "Invalid archive or unsupported CT geometry")
    finally:
        if extracted is not None:
            shutil.rmtree(cleanup, ignore_errors=True)
