# Source API and subfunction reference

[Module guide](../lung/code-reference.md) · [Root overview](../../README.md)

Generated from maintained Python source with `scripts/generate_api_docs.py`. This is a navigation/reference index; subject guides define operation and research boundaries. It imports no application, model or clinical data. Source links include exact lines; direct calls are static names, not a runtime trace.

## [deploy/__init__.py](../../deploy/__init__.py)

Deployment utilities for Day 7.

## [deploy/app.py](../../deploy/app.py)

Experimental localhost API. CLI is the primary validated interface.

#### [lifespan](../../deploy/app.py#L28)

`lifespan(app)`

Static calls (including nested helper bodies): `Path`, `os.getenv`, `load_checkpoint`, `build_model_from_checkpoint`, `create_onnx_session`, `verify_runtime_binding`, `verify_preprocessing_contract`, `str`, `PreprocessConfig`, `ValueError`, `app.state.session.get_inputs`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [health](../../deploy/app.py#L59)

`health()`

Static calls (including nested helper bodies): `app.get`, `getattr`, `HTTPException`.

Explicit raised conditions: `HTTPException`. See source for triggers; called validators may raise additional exceptions.

#### [predict](../../deploy/app.py#L66)

`predict(dicom_zip: UploadFile=File(...))`

Static calls (including nested helper bodies): `app.post`, `File`, `dicom_zip.file.read`, `getattr`, `HTTPException`, `len`, `tempfile.TemporaryDirectory`, `unzip_series_bytes`, `run_deployment_inference`, `io.BytesIO`, `Response`, `zipfile.ZipFile`, `z.write`, `archive.getvalue` (additional calls in source).

Explicit raised conditions: `HTTPException`. See source for triggers; called validators may raise additional exceptions.

## [deploy/cli_infer.py](../../deploy/cli_infer.py)

Implementation module; see the linked source and module guide.

#### [_parse_margin_triplet](../../deploy/cli_infer.py#L18)

`_parse_margin_triplet(raw_value: str) → tuple[float, float, float]`

Static calls (including nested helper bodies): `part.strip`, `len`, `ValueError`, `float`, `raw_value.split`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_build_parser](../../deploy/cli_infer.py#L25)

`_build_parser() → argparse.ArgumentParser`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `parser.add_argument`, `str`.

#### [_preprocess_config_from_args](../../deploy/cli_infer.py#L75)

`_preprocess_config_from_args(args: argparse.Namespace) → PreprocessConfig`

Static calls (including nested helper bodies): `replace`, `PreprocessConfig`, `_parse_margin_triplet`.

#### [main](../../deploy/cli_infer.py#L94)

`main() → int`

Static calls (including nested helper bodies): `_build_parser().parse_args`, `run_deployment_inference`, `dict`, `result.output_paths.report_path.write_text`, `print`, `json.dumps`, `set`, `_build_parser`, `_preprocess_config_from_args`.

## [deploy/inference_runtime.py](../../deploy/inference_runtime.py)

Implementation module; see the linked source and module guide.

### [RuntimePaths](../../deploy/inference_runtime.py#L45)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `mask_volume_path` | `Path` | `required / supplied by caller` |
| `overlay_dir` | `Path` | `required / supplied by caller` |
| `report_path` | `Path` | `required / supplied by caller` |
| `preprocess_report_path` | `Path` | `required / supplied by caller` |
| `validation_report_path` | `Path \| None` | `required / supplied by caller` |

### [DeploymentResult](../../deploy/inference_runtime.py#L54)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `prediction_volume` | `np.ndarray` | `required / supplied by caller` |
| `probabilities_czyx` | `np.ndarray` | `required / supplied by caller` |
| `processed_volume` | `np.ndarray` | `required / supplied by caller` |
| `processed_spacing_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |
| `raw_slice_count` | `int` | `required / supplied by caller` |
| `output_paths` | `RuntimePaths` | `required / supplied by caller` |
| `report` | `dict[str, Any]` | `required / supplied by caller` |

#### [set_deterministic_runtime](../../deploy/inference_runtime.py#L64)

`set_deterministic_runtime(num_threads: int) → None`

Static calls (including nested helper bodies): `max`, `str`, `np.random.seed`, `torch.manual_seed`, `torch.use_deterministic_algorithms`, `torch.set_num_threads`, `int`.

#### [load_checkpoint](../../deploy/inference_runtime.py#L74)

`load_checkpoint(checkpoint_path: str \| Path) → dict[str, Any]`

Static calls (including nested helper bodies): `Path(checkpoint_path).expanduser().resolve`, `torch.load`, `hashlib.sha256(path.read_bytes()).hexdigest`, `Path(checkpoint_path).expanduser`, `hashlib.sha256`, `path.read_bytes`, `Path`.

#### [build_model_from_checkpoint](../../deploy/inference_runtime.py#L81)

`build_model_from_checkpoint(checkpoint: dict[str, Any]) → UNetSmall`

Static calls (including nested helper bodies): `UNetSmall`, `model.load_state_dict`, `model.eval`, `ValueError`, `checkpoint['model_config'].get`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [export_checkpoint_to_onnx](../../deploy/inference_runtime.py#L93)

`export_checkpoint_to_onnx(checkpoint_path: str \| Path, onnx_path: str \| Path, *, opset_version: int=17) → Path`

Static calls (including nested helper bodies): `load_checkpoint`, `build_model_from_checkpoint`, `torch.randn`, `Path(onnx_path).expanduser().resolve`, `destination.parent.mkdir`, `onnx.load`, `onnx.helper.set_model_props`, `onnx.checker.check_model`, `onnx.save`, `int`, `torch.no_grad`, `torch.onnx.export`, `str`, `Path(onnx_path).expanduser` (additional calls in source).

#### [load_and_preprocess_series](../../deploy/inference_runtime.py#L142)

`load_and_preprocess_series(series_dir: str \| Path, preprocess_config: PreprocessConfig) → tuple[np.ndarray, tuple[float, float, float], dict[str, Any]]`

Static calls (including nested helper bodies): `time.perf_counter`, `load_dicom_series`, `run_preprocessing_pipeline`, `geometry_transform`, `result.crop_bbox_zyx.to_dict`, `list`, `asdict`, `result.processed_volume.astype`, `tuple`, `int`, `float`.

#### [build_input_stack_volume](../../deploy/inference_runtime.py#L177)

`build_input_stack_volume(processed_volume: np.ndarray) → np.ndarray`

Static calls (including nested helper bodies): `np.stack(stacks, axis=0).astype`, `build_25d_stack`, `range`, `np.stack`, `int`.

#### [_resize_stack_batch](../../deploy/inference_runtime.py#L185)

`_resize_stack_batch(batch: np.ndarray, height: int, width: int) → np.ndarray`

Static calls (including nested helper bodies): `torch.from_numpy`, `F.interpolate`, `resized.numpy().astype`, `batch.astype`, `resized.numpy`.

#### [_apply_temperature_numpy](../../deploy/inference_runtime.py#L193)

`_apply_temperature_numpy(logits: np.ndarray, temperature: float) → np.ndarray`

Static calls (including nested helper bodies): `logits.astype`, `max`, `float`.

#### [_softmax_numpy](../../deploy/inference_runtime.py#L197)

`_softmax_numpy(logits: np.ndarray) → np.ndarray`

Static calls (including nested helper bodies): `logits.astype`, `np.exp`, `logits.max`, `np.clip`, `exp.sum`.

#### [validate_onnx_equivalence](../../deploy/inference_runtime.py#L204)

`validate_onnx_equivalence(checkpoint_path: str \| Path, onnx_path: str \| Path, sample_batch: np.ndarray, *, num_threads: int=1, temperature: float=1.0) → dict[str, Any]`

Static calls (including nested helper bodies): `load_checkpoint`, `build_model_from_checkpoint`, `create_onnx_session`, `verify_runtime_binding`, `_apply_temperature_numpy`, `np.abs`, `torch.no_grad`, `float`, `bool`, `session.run`, `_softmax_numpy`, `int`, `diff.max`, `diff.mean` (additional calls in source).

#### [create_onnx_session](../../deploy/inference_runtime.py#L255)

`create_onnx_session(onnx_path: str \| Path, *, num_threads: int=1) → ort.InferenceSession`

Static calls (including nested helper bodies): `ort.SessionOptions`, `max`, `ort.InferenceSession`, `int`, `str`, `Path(onnx_path).expanduser().resolve`, `Path(onnx_path).expanduser`, `Path`.

#### [verify_runtime_binding](../../deploy/inference_runtime.py#L270)

`verify_runtime_binding(checkpoint, session)`

Static calls (including nested helper bodies): `session.get_modelmeta().custom_metadata_map.get`, `ValueError`, `session.get_modelmeta`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [verify_preprocessing_contract](../../deploy/inference_runtime.py#L280)

`verify_preprocessing_contract(checkpoint, config)`

Static calls (including nested helper bodies): `checkpoint.get`, `ValueError`, `json.loads`, `json.dumps`, `asdict`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [run_onnx_segmentation](../../deploy/inference_runtime.py#L290)

`run_onnx_segmentation(session: ort.InferenceSession, stack_volume: np.ndarray, *, model_height: int, model_width: int, batch_size: int=1, original_hw: tuple[int, int], temperature: float=1.0) → np.ndarray`

Static calls (including nested helper bodies): `range`, `np.concatenate(outputs, axis=0).astype`, `ValueError`, `int`, `_resize_stack_batch`, `_apply_temperature_numpy`, `_softmax_numpy`, `outputs.append`, `tuple`, `probabilities.astype`, `np.concatenate`, `session.run`, `np.clip`, `F.interpolate` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [save_prediction_volume](../../deploy/inference_runtime.py#L330)

`save_prediction_volume(prediction_volume: np.ndarray, *, spacing_zyx: tuple[float, float, float], output_path: str \| Path, output_format: str) → Path`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `destination.parent.mkdir`, `ValueError`, `np.savez_compressed`, `save_nifti_volume`, `Path(output_path).expanduser`, `prediction_volume.astype`, `np.asarray`, `Path`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [run_deployment_inference](../../deploy/inference_runtime.py#L353)

`run_deployment_inference(*, series_dir: str \| Path, checkpoint_path: str \| Path, onnx_path: str \| Path, output_dir: str \| Path, preprocess_config: PreprocessConfig, batch_size: int=1, num_threads: int=1, export_onnx: bool=False, validate_onnx: bool=True, mask_output_format: str='npz', save_overlays: bool=True, enable_postprocess: bool=True, runtime_session=None, runtime_checkpoint=None) → DeploymentResult`

Static calls (including nested helper bodies): `time.perf_counter`, `set_deterministic_runtime`, `verify_preprocessing_contract`, `int`, `float`, `load_and_preprocess_series`, `build_input_stack_volume`, `_resize_stack_batch`, `verify_runtime_binding`, `run_onnx_segmentation`, `compute_entropy_uncertainty`, `Path(output_dir).expanduser().resolve`, `output_root.mkdir`, `PreprocessResult` (additional calls in source).

Explicit raised conditions: `RuntimeError`. See source for triggers; called validators may raise additional exceptions.

#### [load_reference_labels](../../deploy/inference_runtime.py#L568)

`load_reference_labels(processed_dir: str \| Path) → np.ndarray \| None`

Static calls (including nested helper bodies): `candidate.exists`, `np.load`, `data['pseudo_labels'].astype`, `Path(processed_dir).expanduser().resolve`, `Path(processed_dir).expanduser`, `Path`.

#### [attach_reference_metrics](../../deploy/inference_runtime.py#L580)

`attach_reference_metrics(report: dict[str, Any], prediction_volume: np.ndarray, reference_labels: np.ndarray \| None) → dict[str, Any]`

Static calls (including nested helper bodies): `compute_segmentation_metrics`, `dict`, `torch.from_numpy`, `prediction_volume.astype`, `reference_labels.astype`.

#### [unzip_series_bytes](../../deploy/inference_runtime.py#L597)

`unzip_series_bytes(payload: bytes, *, extraction_root: Path \| None=None) → Path`

Validate and extract one series into an owned or caller-managed empty root.

A caller supplying ``extraction_root`` owns its lifetime; the returned series
may be nested arbitrarily. Never infer the cleanup root from member names.

Static calls (including nested helper bodies): `len`, `ValueError`, `Path`, `Path(extraction_root).resolve`, `any`, `directories.pop`, `tempfile.mkdtemp`, `temp_dir.is_dir`, `temp_dir.iterdir`, `zipfile.ZipFile`, `set`, `archive.infolist`, `archive.extractall`, `io.BytesIO` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [deploy/mhcra_bridge.py](../../deploy/mhcra_bridge.py)

Synthetic-only inspection bundles for LOVISA; retained MHCRA tissue-mask interface.

#### [checksum](../../deploy/mhcra_bridge.py#L32)

`checksum(path)`

Static calls (including nested helper bodies): `hashlib.sha256(Path(path).read_bytes()).hexdigest`, `hashlib.sha256`, `Path(path).read_bytes`, `Path`.

#### [identifier](../../deploy/mhcra_bridge.py#L36)

`identifier(value)`

Static calls (including nested helper bodies): `re.fullmatch`, `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [verify_synthetic](../../deploy/mhcra_bridge.py#L42)

`verify_synthetic(series)`

Static calls (including nested helper bodies): `Path(series).resolve`, `series.with_name`, `json.loads`, `hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest`, `marker.read_text`, `checksum`, `ValueError`, `Path`, `sorted`, `p.is_file`, `manifest.get`, `hashlib.sha256`, `series.iterdir`, `json.dumps(actual, sort_keys=True).encode` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [export_bundle](../../deploy/mhcra_bridge.py#L52)

`export_bundle(*, series, checkpoint, onnx, destination, patient_id, study_id)`

Static calls (including nested helper bodies): `verify_synthetic`, `load_dicom_series`, `Path(destination).resolve`, `destination.mkdir`, `run_deployment_inference`, `artifact`, `previews.mkdir`, `(np.clip((volume.volume_hu + 200) / 1200, 0, 1) * 255).astype`, `range`, `manifest.write_text`, `identifier`, `ValueError`, `np.load`, `data['spacing_zyx'].astype` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [export_bundle.artifact](../../deploy/mhcra_bridge.py#L75)

`artifact(path, role, slice_index=None)`

Static calls (including nested helper bodies): `artifacts.append`, `path.relative_to(destination).as_posix`, `checksum`, `path.stat`, `path.relative_to`.

#### [synthetic_demo](../../deploy/mhcra_bridge.py#L122)

`synthetic_demo(destination, patient_id, study_id)`

Static calls (including nested helper bodies): `Path(destination).resolve`, `destination.mkdir`, `generate`, `prepare`, `subprocess.run`, `export_bundle`, `Path`, `str`.

#### [main](../../deploy/mhcra_bridge.py#L141)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `print`, `synthetic_demo`, `export_bundle`, `all`, `p.error`.

## [deploy/mhcra_lung_bridge.py](../../deploy/mhcra_lung_bridge.py)

Offline generated-synthetic nodule jobs for LOVISA; legacy MHCRA entry point, no approval.

#### [identifier](../../deploy/mhcra_lung_bridge.py#L13)

`identifier(value)`

Static calls (including nested helper bodies): `re.fullmatch`, `argparse.ArgumentTypeError`.

Explicit raised conditions: `argparse.ArgumentTypeError`. See source for triggers; called validators may raise additional exceptions.

#### [generate_bundle](../../deploy/mhcra_lung_bridge.py#L21)

`generate_bundle(destination, patient_id, study_id, *, mode='fixture', model_dir=None, device='cpu', progress=None)`

Run selected real/fixture detector on generated pixels; export pending v2.

Static calls (including nested helper bodies): `report`, `identifier`, `Path`, `destination.mkdir`, `generate_chest`, `detect_study`, `save_workspace`, `export_synthetic_exchange`, `ValueError`, `torch.set_num_threads`, `MonaiDetector`, `PhantomDetector`, `os.environ.get`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [main](../../deploy/mhcra_lung_bridge.py#L68)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `generate_bundle`, `print`.

## [scripts/benchmark_intel.py](../../scripts/benchmark_intel.py)

Full model OpenVINO CPU/NPU comparison on identical held-out tensors.
Requires openvino, numpy, onnxruntime; no torch dependency in the Intel environment.

#### [softmax](../../scripts/benchmark_intel.py#L17)

`softmax(x)`

Static calls (including nested helper bodies): `np.exp`, `e.sum`, `x.max`.

#### [scores](../../scripts/benchmark_intel.py#L22)

`scores(pred, target)`

Static calls (including nested helper bodies): `range`, `int`, `str`, `float`, `dice.values`, `a.sum`, `b.sum`, `np.mean`, `np.logical_and(a, b).sum`, `np.logical_and`.

#### [peak_memory](../../scripts/benchmark_intel.py#L32)

`peak_memory()`

Static calls (including nested helper bodies): `Counters`, `ctypes.sizeof`, `ctypes.windll.psapi.GetProcessMemoryInfo`, `platform.system`, `ctypes.POINTER`, `ctypes.windll.kernel32.GetCurrentProcess`, `ctypes.byref`, `int`.

### [peak_memory.Counters](../../scripts/benchmark_intel.py#L38)

Class contract is defined by the fields and methods below.

#### [plugged_in_state](../../scripts/benchmark_intel.py#L69)

`plugged_in_state()`

Static calls (including nested helper bodies): `PowerStatus`, `{0: 'battery', 1: 'AC connected', 255: 'unknown'}.get`, `platform.system`, `ctypes.windll.kernel32.GetSystemPowerStatus`, `ctypes.byref`.

### [plugged_in_state.PowerStatus](../../scripts/benchmark_intel.py#L75)

Class contract is defined by the fields and methods below.

#### [benchmark](../../scripts/benchmark_intel.py#L93)

`benchmark(model_path, input_path, output, runs=30)`

Static calls (including nested helper bodies): `np.load`, `ov.Core`, `ort.SessionOptions`, `time.perf_counter`, `ort.InferenceSession`, `runtimes.append`, `Path(output).parent.mkdir`, `Path(output).write_text`, `print`, `hashlib.sha256(Path(model_path).read_bytes()).hexdigest`, `hashlib.sha256(Path(input_path).read_bytes()).hexdigest`, `list`, `len`, `platform.platform` (additional calls in source).

## [scripts/benchmark_lung.py](../../scripts/benchmark_lung.py)

Full local detection latency on unchanged inputs; no clinical or NPU claims.

#### [main](../../scripts/benchmark_lung.py#L14)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `torch.set_num_threads`, `time.perf_counter`, `MonaiDetector`, `run`, `range`, `Path(a.output).parent.mkdir`, `Path(a.output).write_text`, `print`, `p.error`, `detect_study`, `times.append` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [main.run](../../scripts/benchmark_lung.py#L33)

`run()`

Static calls (including nested helper bodies): `detect_study`, `torch.cuda.synchronize`.

## [scripts/check.py](../../scripts/check.py)

Required CPU checks; missing tooling is an error, never a silent skip.

#### [main](../../scripts/check.py#L10)

`main()`

Static calls (including nested helper bodies): `subprocess.run`, `str`.

## [scripts/check_docs.py](../../scripts/check_docs.py)

Check maintained Markdown links and heading anchors without network access.

This intentionally checks ordinary inline links, not a complete Markdown grammar.
It excludes fenced examples and never walks ignored datasets or environments.

#### [prose](../../scripts/check_docs.py#L18)

`prose(text)`

Remove fenced code so example links/headings are not treated as active.

Static calls (including nested helper bodies): `text.splitlines`, `'\n'.join`, `re.match`, `marker.group`, `output.append`, `len`.

#### [anchors](../../scripts/check_docs.py#L35)

`anchors(text)`

Approximate GitHub heading IDs, including repeated headings and Unicode.

Static calls (including nested helper bodies): `prose(text).splitlines`, `result.update`, `set`, `HEADING.match`, `re.sub`, `html.unescape(re.sub('<[^>]+>', '', label)).lower`, `''.join((c for c in label if c.isalnum() or c in '_ -')).replace`, `counts.get`, `result.add`, `re.findall`, `prose`, `match.group`, `html.unescape`, `''.join` (additional calls in source).

#### [documents](../../scripts/check_docs.py#L52)

`documents(root)`

Select maintained guides only; local runtime Markdown is not publication.

Static calls (including nested helper bodies): `Path`, `sorted`, `root.glob`, `(root / 'docs').rglob`, `(root / 'third_party').rglob`, `p.is_file`.

#### [validate](../../scripts/check_docs.py#L69)

`validate(root)`

Return broken local files/anchors; HTTPS links are deliberately not fetched.

Static calls (including nested helper bodies): `Path(root).resolve`, `documents`, `LINK.finditer`, `Path`, `prose`, `match.group(1).strip`, `urlsplit`, `file.read_text`, `(file.parent / unquote(url.path)).resolve`, `path.exists`, `errors.append`, `match.group`, `path.suffix.lower`, `anchors` (additional calls in source).

#### [main](../../scripts/check_docs.py#L91)

`main()`

Static calls (including nested helper bodies): `validate`, `print`, `ValueError`, `Path(__file__).resolve`, `'\n'.join`, `len`, `Path`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/classical_baseline.py](../../scripts/classical_baseline.py)

Compatibility wrapper for the unified versioned case preparation CLI.
Use --series-dir and --output-dir; old threshold flags are no longer accepted.

## [scripts/evaluate_public_lidc.py](../../scripts/evaluate_public_lidc.py)

One-series reader-level localization smoke against official LIDC XML contours.

Not LUNA scoring, reader consensus, pathology or independent clinical validation.
Annotations are used only after model inference and never to select predictions.

#### [annotation_boxes](../../scripts/evaluate_public_lidc.py#L19)

`annotation_boxes(xml_path, study)`

Map included >=3-mm contour observations by exact hashed source SOP ID.

Static calls (including nested helper bodies): `Path`, `path.read_bytes`, `ET.fromstring`, `root.iter`, `enumerate`, `ValueError`, `root.findall`, `session.findall`, `path.stat`, `raw.upper`, `e.tag.rsplit`, `nodule.findall`, `nodule.find`, `roi.findtext` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [evaluate](../../scripts/evaluate_public_lidc.py#L67)

`evaluate(workspace, xml)`

Static calls (including nested helper bodies): `load_workspace`, `annotation_boxes`, `len`, `json.loads`, `integrity.get`, `sorted`, `dict`, `(Path(workspace) / 'integrity.json').read_text`, `np.array`, `np.asarray`, `rows.append`, `sha256`, `sum`, `np.all` (additional calls in source).

#### [main](../../scripts/evaluate_public_lidc.py#L118)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `evaluate`, `Path(a.output).write_text`, `print`, `json.dumps`, `Path`, `report.items`.

## [scripts/export_verified.py](../../scripts/export_verified.py)

Implementation module; see the linked source and module guide.

## [scripts/fetch_lidc_demo.py](../../scripts/fetch_lidc_demo.py)

Explicit setup-only TCIA public download for the fixed LIDC-IDRI-0002 demo.

Local inference never calls this script. Download permission is not clinical review.
TCIA deidentified dates are retained in original files, never interpreted as real dates.

#### [download](../../scripts/fetch_lidc_demo.py#L19)

`download(url, path, limit)`

Stream a TLS-verified public file to a bounded exclusive temporary file.

Static calls (including nested helper bodies): `path.with_suffix`, `temp.rename`, `temp.unlink`, `urllib.request.urlopen`, `temp.open`, `source.read`, `len`, `out.write`, `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [main](../../scripts/fetch_lidc_demo.py#L35)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `a.output.resolve`, `root.mkdir`, `urllib.parse.urlencode`, `(root / 'metadata.json').write_text`, `download`, `series.mkdir`, `(root / 'approval.json').write_text`, `(root / 'download-sha256.json').write_text`, `print`, `ValueError`, `dict` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/generate_api_docs.py](../../scripts/generate_api_docs.py)

Regenerate source-linked class/function references without importing the app.

Run --write after intentional source changes; --check fails on stale documentation.
Annotations and docstrings describe code, not verified clinical capabilities.

#### [cell](../../scripts/generate_api_docs.py#L14)

`cell(text)`

Keep source syntax inside one Markdown table cell.

Static calls (including nested helper bodies): `' '.join(str(text).split()).replace('\|', '\\\|').replace`, `' '.join(str(text).split()).replace`, `' '.join`, `str(text).split`, `str`.

#### [source_files](../../scripts/generate_api_docs.py#L19)

`source_files(root)`

Select maintained implementation, interfaces and scripts, not tests/data.

Static calls (including nested helper bodies): `sorted`, `(root / name).rglob`, `p.is_file`.

#### [render](../../scripts/generate_api_docs.py#L35)

`render(root)`

Derive signatures, declared fields, docstrings and direct calls from AST.

Static calls (including nested helper bodies): `source_files`, `path.relative_to(root).as_posix`, `ast.parse`, `walk`, `'\n'.join(lines).rstrip`, `path.read_text`, `(root / 'docs/CODE_REFERENCE.md').is_file`, `path.relative_to`, `ast.get_docstring`, `isinstance`, `'\n'.join`, `lines.extend`, `lines.append`, `ast.walk` (additional calls in source).

#### [render.walk](../../scripts/generate_api_docs.py#L64)

`walk(nodes, prefix='')`

Static calls (including nested helper bodies): `isinstance`, `lines.extend`, `walk`, `lines.append`, `ast.get_docstring`, `ast.walk`, `sorted`, `ast.iter_child_nodes`, `ast.unparse`, `calls.append`, `cell`, `len`, `', '.join`.

#### [main](../../scripts/generate_api_docs.py#L160)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `parser.add_mutually_exclusive_group`, `action.add_argument`, `parser.parse_args`, `render`, `target.parent.mkdir`, `target.write_text`, `print`, `Path(__file__).resolve`, `target.relative_to`, `SystemExit`, `target.is_file`, `target.read_text`, `Path`.

Explicit raised conditions: `SystemExit`. See source for triggers; called validators may raise additional exceptions.

## [scripts/generate_fixture.py](../../scripts/generate_fixture.py)

Generate synthetic CT; no source patient data or copied headers.

#### [generate](../../scripts/generate_fixture.py#L12)

`generate(destination, depth=20, size=48, oblique=False, compressed=False)`

Static calls (including nested helper bodies): `Path`, `destination.mkdir`, `any`, `np.array`, `np.cross`, `np.sqrt`, `range`, `destination.iterdir`, `ValueError`, `generate_uid`, `FileMetaDataset`, `FileDataset`, `list`, `np.where` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/illustrate_lung.py](../../scripts/illustrate_lung.py)

Reproduce a figure from generated source pixels and fixture annotations, not patient images.

#### [main](../../scripts/illustrate_lung.py#L17)

`main()`

Static calls (including nested helper bodies): `tempfile.TemporaryDirectory`, `detect_study`, `plt.subplots`, `Caliper`, `zip`, `fig.suptitle`, `fig.text`, `fig.tight_layout`, `fig.savefig`, `plt.close`, `print`, `generate_chest`, `PhantomDetector`, `overlay_slice` (additional calls in source).

## [scripts/illustrate_workbench.py](../../scripts/illustrate_workbench.py)

Plot source/overlay previews from a generated-synthetic MHCRA bundle.

#### [illustrate](../../scripts/illustrate_workbench.py#L17)

`illustrate(bundle, output)`

Static calls (including nested helper bodies): `zipfile.ZipFile`, `json.loads`, `plt.figure`, `fig.add_gridspec`, `enumerate`, `fig.add_subplot`, `ax.barh`, `ax.set_title`, `ax.set_xlabel`, `ax.xaxis.set_major_locator`, `ax.xaxis.set_major_formatter`, `ax.spines[['top', 'right']].set_visible`, `ax.tick_params`, `details.axis` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/infer.py](../../scripts/infer.py)

Implementation module; see the linked source and module guide.

#### [_build_parser](../../scripts/infer.py#L30)

`_build_parser() → argparse.ArgumentParser`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `parser.add_argument`, `str`.

#### [_predict_probabilities](../../scripts/infer.py#L60)

`_predict_probabilities(model: UNetSmall, images: torch.Tensor, device: torch.device, uncertainty_method: str, temperature: float) → torch.Tensor`

Static calls (including nested helper bodies): `images.to`, `apply_temperature`, `torch.softmax`, `model`, `torch.flip`, `float`, `len`.

#### [_slice_metrics](../../scripts/infer.py#L85)

`_slice_metrics(prediction_volume: np.ndarray, target_volume: np.ndarray, slice_indices: list[int]) → list[dict[str, float \| int]]`

Static calls (including nested helper bodies): `enumerate`, `compute_segmentation_metrics`, `metrics.append`, `torch.from_numpy`, `int`, `float`.

#### [main](../../scripts/infer.py#L107)

`main() → int`

Static calls (including nested helper bodies): `_build_parser().parse_args`, `Path(args.index_path).expanduser().resolve`, `Path(args.checkpoint).expanduser().resolve`, `Path(args.output_dir).expanduser().resolve`, `Path(args.processed_dir).expanduser().resolve`, `output_dir.mkdir`, `processed_dir.mkdir`, `torch.load`, `UNetSmall`, `model.load_state_dict`, `model.eval`, `torch.device`, `model.to`, `float` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/inspect_series.py](../../scripts/inspect_series.py)

Implementation module; see the linked source and module guide.

#### [_build_parser](../../scripts/inspect_series.py#L16)

`_build_parser() → argparse.ArgumentParser`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `parser.add_argument`.

#### [main](../../scripts/inspect_series.py#L40)

`main() → int`

Static calls (including nested helper bodies): `_build_parser`, `parser.parse_args`, `load_app_config`, `load_dicom_series`, `config.output_dir.mkdir`, `write_metadata_json`, `save_hu_histogram`, `save_montage`, `print`, `os.environ.setdefault`, `json.dumps`, `show_axial_scroll`, `volume.metadata.to_dict`, `tuple` (additional calls in source).

## [scripts/lung_hardware.py](../../scripts/lung_hardware.py)

Report actual hardware; never infer present devices from historical benchmarks.

#### [inspect_hardware](../../scripts/lung_hardware.py#L10)

`inspect_hardware()`

Static calls (including nested helper bodies): `platform.platform`, `platform.processor`, `torch.cuda.is_available`, `importlib.metadata.version`, `torch.cuda.get_device_name`, `ov.Core`, `range`, `torch.cuda.device_count`.

## [scripts/prepare_case.py](../../scripts/prepare_case.py)

Versioned, sanitized preprocessing and pseudo-label manifest CLI.

#### [prepare](../../scripts/prepare_case.py#L26)

`prepare(series, destination)`

Static calls (including nested helper bodies): `Path(destination).resolve`, `destination.mkdir`, `load_dicom_series`, `PreprocessConfig`, `SegmentationConfig`, `run_preprocessing_pipeline`, `generate_classical_masks`, `save_npz_volume`, `np.savez_compressed`, `assign_single_case_slice_splits`, `CT25DCase`, `build_case_index`, `frame.drop`, `frame.to_csv` (additional calls in source).

#### [main](../../scripts/prepare_case.py#L131)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `prepare`.

## [scripts/preprocess_series.py](../../scripts/preprocess_series.py)

Compatibility wrapper for the unified versioned case preparation CLI.
Use --series-dir and --output-dir; old threshold flags are no longer accepted.

## [scripts/smoke_lung.py](../../scripts/smoke_lung.py)

Actual local inference smoke on generated CT; never approves a report or measures clinical accuracy.

#### [main](../../scripts/smoke_lung.py#L14)

`main()`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_argument`, `p.parse_args`, `torch.set_num_threads`, `time.perf_counter`, `Path(a.output).parent.mkdir`, `Path(a.output).write_text`, `print`, `MonaiDetector`, `PhantomDetector`, `p.error`, `tempfile.TemporaryDirectory`, `Path`, `detect_study` (additional calls in source).

Explicit raised conditions: `AssertionError`. See source for triggers; called validators may raise additional exceptions.

## [scripts/train.py](../../scripts/train.py)

Implementation module; see the linked source and module guide.

### [ResizeConfig](../../scripts/train.py#L32)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `height` | `int` | `required / supplied by caller` |
| `width` | `int` | `required / supplied by caller` |

### [ResizedSegmentationDataset](../../scripts/train.py#L37)

Class contract is defined by the fields and methods below.

#### [ResizedSegmentationDataset.__init__](../../scripts/train.py#L38)

`__init__(self, base_dataset: CT25DDataset, resize: ResizeConfig) → None`

#### [ResizedSegmentationDataset.__len__](../../scripts/train.py#L42)

`__len__(self) → int`

Static calls (including nested helper bodies): `len`.

#### [ResizedSegmentationDataset.__getitem__](../../scripts/train.py#L45)

`__getitem__(self, index: int) → dict[str, object]`

Static calls (including nested helper bodies): `sample['image'].float().unsqueeze`, `sample['mask'].long().unsqueeze(0).unsqueeze(0).float`, `sample['image'].float`, `sample['mask'].long().unsqueeze(0).unsqueeze`, `F.interpolate`, `sample['mask'].long().unsqueeze`, `sample['mask'].long`.

#### [_parse_hw](../../scripts/train.py#L74)

`_parse_hw(raw_value: str) → ResizeConfig`

Static calls (including nested helper bodies): `ResizeConfig`, `part.strip`, `len`, `ValueError`, `raw_value.split`, `int`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_set_seed](../../scripts/train.py#L81)

`_set_seed(seed: int, num_threads: int) → None`

Static calls (including nested helper bodies): `random.seed`, `np.random.seed`, `torch.manual_seed`, `torch.use_deterministic_algorithms`, `torch.set_num_threads`, `int`.

#### [_build_parser](../../scripts/train.py#L89)

`_build_parser() → argparse.ArgumentParser`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `parser.add_argument`, `parser.parse_known_args`, `json.loads`, `','.join`, `parser.set_defaults`, `Path(known.config).read_text`, `map`, `str`, `Path`.

#### [_make_loader](../../scripts/train.py#L132)

`_make_loader(dataset: Dataset, batch_size: int, shuffle: bool, num_workers: int, seed: int) → DataLoader`

Static calls (including nested helper bodies): `torch.Generator`, `generator.manual_seed`, `DataLoader`.

#### [_estimate_class_weights](../../scripts/train.py#L147)

`_estimate_class_weights(dataset: Dataset, num_classes: int) → torch.Tensor`

Static calls (including nested helper bodies): `torch.zeros`, `range`, `weights.to`, `len`, `dataset[index]['mask'].reshape`, `torch.bincount(mask, minlength=num_classes).to`, `counts.sum`, `counts.clamp_min`, `weights.mean().clamp_min`, `torch.bincount`, `weights.mean`.

#### [_run_epoch](../../scripts/train.py#L157)

`_run_epoch(model: UNetSmall, loader: DataLoader, optimizer: torch.optim.Optimizer \| None, device: torch.device, num_classes: int, class_weights: torch.Tensor \| None) → dict[str, float]`

Static calls (including nested helper bodies): `model.train`, `max`, `compute_segmentation_metrics`, `batch['image'].to`, `batch['mask'].to`, `predictions.append`, `targets.append`, `len`, `torch.cat`, `torch.set_grad_enabled`, `model`, `combined_dice_ce_loss`, `float`, `int` (additional calls in source).

#### [_collect_logits_and_targets](../../scripts/train.py#L201)

`_collect_logits_and_targets(model: UNetSmall, loader: DataLoader, device: torch.device) → tuple[torch.Tensor, torch.Tensor]`

Static calls (including nested helper bodies): `model.eval`, `torch.no_grad`, `torch.cat`, `batch['image'].to`, `batch['mask'].to`, `model`, `all_logits.append`, `all_targets.append`, `logits.cpu`, `masks.cpu`.

#### [main](../../scripts/train.py#L217)

`main() → int`

Static calls (including nested helper bodies): `_build_parser().parse_args`, `_parse_hw`, `Path(args.output_dir).expanduser().resolve`, `Path(args.model_dir).expanduser().resolve`, `Path(args.index_path).expanduser().resolve`, `output_dir.mkdir`, `model_dir.mkdir`, `_set_seed`, `torch.device`, `build_default_train_transforms`, `CT25DDataset`, `ResizedSegmentationDataset`, `_make_loader`, `_estimate_class_weights(train_dataset, num_classes=4).to` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/baselines/__init__.py](../../src/baselines/__init__.py)

Implementation module; see the linked source and module guide.

## [src/baselines/classical_seg.py](../../src/baselines/classical_seg.py)

Implementation module; see the linked source and module guide.

### [SegmentationResult](../../src/baselines/classical_seg.py#L14)

Container for 3D masks, pseudo labels, and adaptive-selection diagnostics.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `bone_mask_3d` | `np.ndarray` | `required / supplied by caller` |
| `brain_mask_3d` | `np.ndarray` | `required / supplied by caller` |
| `pseudo_labels_3d` | `np.ndarray` | `required / supplied by caller` |
| `brain_selection` | `dict[str, Any]` | `required / supplied by caller` |

### [BrainCandidate](../../src/baselines/classical_seg.py#L24)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `mask_3d` | `np.ndarray` | `required / supplied by caller` |
| `stats` | `dict[str, float \| int]` | `required / supplied by caller` |
| `score` | `float` | `required / supplied by caller` |
| `params` | `dict[str, float \| int]` | `required / supplied by caller` |
| `head_ratio` | `float` | `required / supplied by caller` |
| `overlap_ratio` | `float` | `required / supplied by caller` |

#### [_connected_components](../../src/baselines/classical_seg.py#L33)

`_connected_components(mask: np.ndarray) → tuple[np.ndarray, int]`

Static calls (including nested helper bodies): `ndimage.generate_binary_structure`, `ndimage.label`.

#### [_remove_small_components](../../src/baselines/classical_seg.py#L38)

`_remove_small_components(mask: np.ndarray, min_size: int) → np.ndarray`

Static calls (including nested helper bodies): `_connected_components`, `np.arange`, `ndimage.sum`, `np.isin`, `mask.astype`, `np.zeros_like`, `np.asarray`, `int`.

#### [_largest_component](../../src/baselines/classical_seg.py#L53)

`_largest_component(mask: np.ndarray) → np.ndarray`

Static calls (including nested helper bodies): `_connected_components`, `np.arange`, `ndimage.sum`, `int`, `np.zeros_like`, `np.argmax`.

#### [_postprocess_binary_mask](../../src/baselines/classical_seg.py#L64)

`_postprocess_binary_mask(mask: np.ndarray, opening_iterations: int, closing_iterations: int, fill_holes: bool, min_component_voxels: int, keep_largest_component: bool) → np.ndarray`

Generic plausibility cleanup used by both bone and brain candidates.

Static calls (including nested helper bodies): `ndimage.generate_binary_structure`, `mask.astype`, `_remove_small_components`, `cleaned.astype`, `ndimage.binary_opening`, `ndimage.binary_closing`, `ndimage.binary_fill_holes`, `_largest_component`, `int`.

#### [bone_mask](../../src/baselines/classical_seg.py#L94)

`bone_mask(volume_hu: np.ndarray, threshold_hu: float=300.0, opening_iterations: int=1, closing_iterations: int=1, min_component_voxels: int=64, keep_largest_component: bool=True) → np.ndarray`

Create a skull/bone candidate mask from HU threshold.

Static calls (including nested helper bodies): `_postprocess_binary_mask`, `float`.

#### [_brain_candidate_mask](../../src/baselines/classical_seg.py#L115)

`_brain_candidate_mask(volume_hu: np.ndarray, *, bone_mask_3d: np.ndarray \| None, window_center: float, window_width: float, norm_min: float, norm_max: float, head_threshold_hu: float, opening_iterations: int, closing_iterations: int, fill_holes: bool, min_component_voxels: int, keep_largest_component: bool) → np.ndarray`

Static calls (including nested helper bodies): `np.empty_like`, `range`, `_postprocess_binary_mask`, `ValueError`, `apply_window`, `float`, `bone_mask_3d.astype`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [summarize_mask_quality](../../src/baselines/classical_seg.py#L159)

`summarize_mask_quality(mask_3d: np.ndarray, spacing_zyx: tuple[float, float, float]) → dict[str, float \| int]`

Compute non-GT evaluation metrics for a binary 3D mask.

Static calls (including nested helper bodies): `mask_3d.astype`, `int`, `float`, `mask_bool.sum`, `_contiguous_non_empty_runs`, `_connected_components`, `np.count_nonzero`, `np.arange`, `ndimage.sum`, `np.max`, `max`, `len`.

#### [_brain_candidate_score](../../src/baselines/classical_seg.py#L197)

`_brain_candidate_score(candidate_mask: np.ndarray, *, bone_mask_3d: np.ndarray, volume_hu: np.ndarray) → BrainCandidate`

Static calls (including nested helper bodies): `summarize_mask_quality`, `float`, `BrainCandidate`, `candidate_mask.astype`, `np.logical_and`, `np.logical_or`, `max`, `candidate_mask.astype(bool).sum`, `bone_mask_3d.astype`, `head_mask.sum`.

#### [select_adaptive_brain_mask](../../src/baselines/classical_seg.py#L237)

`select_adaptive_brain_mask(volume_hu: np.ndarray, *, bone_mask_3d: np.ndarray, window_center: float, window_width: float, norm_min: float, norm_max: float, head_threshold_hu: float, opening_iterations: int, closing_iterations: int, fill_holes: bool, min_component_voxels: int, keep_largest_component: bool) → tuple[np.ndarray, dict[str, Any]]`

Static calls (including nested helper bodies): `sorted`, `max`, `_brain_candidate_mask`, `BrainCandidate`, `float`, `int`, `best.mask_3d.astype`, `len`, `min`, `relaxed_candidate.astype`, `summarize_mask_quality`, `enumerate`, `_brain_candidate_score`, `candidates.append`.

#### [brain_mask](../../src/baselines/classical_seg.py#L362)

`brain_mask(volume_hu: np.ndarray, window_center: float=40.0, window_width: float=120.0, norm_min: float=0.05, norm_max: float=0.95, head_threshold_hu: float=-300.0, opening_iterations: int=1, closing_iterations: int=2, fill_holes: bool=True, min_component_voxels: int=256, keep_largest_component: bool=True, bone_mask_3d: np.ndarray \| None=None) → np.ndarray`

Create a brain-ish mask using adaptive threshold selection around the brain window.

Static calls (including nested helper bodies): `select_adaptive_brain_mask`, `bone_mask`, `max`, `float`.

#### [generate_classical_masks](../../src/baselines/classical_seg.py#L404)

`generate_classical_masks(volume_hu: np.ndarray, segmentation_config: SegmentationConfig) → SegmentationResult`

Run day-3 classical segmentation and return binary masks + label volume.

Static calls (including nested helper bodies): `bone_mask`, `select_adaptive_brain_mask`, `brain_uint8.astype`, `np.zeros_like`, `SegmentationResult`, `max`, `brain_exclusion_bone.astype`, `bone.astype`, `brain.astype`, `float`, `int`.

#### [_contiguous_non_empty_runs](../../src/baselines/classical_seg.py#L466)

`_contiguous_non_empty_runs(slice_counts: np.ndarray) → list[int]`

Static calls (including nested helper bodies): `runs.append`, `int`.

## [src/calibration.py](../../src/calibration.py)

Implementation module; see the linked source and module guide.

#### [apply_temperature](../../src/calibration.py#L7)

`apply_temperature(logits: torch.Tensor, temperature: float) → torch.Tensor`

Static calls (including nested helper bodies): `max`, `float`.

#### [negative_log_likelihood](../../src/calibration.py#L12)

`negative_log_likelihood(logits: torch.Tensor, targets: torch.Tensor) → float`

Static calls (including nested helper bodies): `float`, `F.cross_entropy(logits, targets.long()).item`, `F.cross_entropy`, `targets.long`.

#### [expected_calibration_error](../../src/calibration.py#L16)

`expected_calibration_error(probabilities: torch.Tensor, targets: torch.Tensor, *, num_bins: int=10) → float`

Static calls (including nested helper bodies): `probabilities.permute(0, 2, 3, 1).reshape`, `targets.reshape`, `flat_probs.max`, `predictions.eq`, `torch.linspace`, `torch.tensor`, `zip`, `float`, `accuracies[in_bin].float().mean`, `confidences[in_bin].mean`, `ece.item`, `probabilities.permute`, `torch.any`, `accuracies[in_bin].float` (additional calls in source).

#### [fit_temperature](../../src/calibration.py#L41)

`fit_temperature(logits: torch.Tensor, targets: torch.Tensor, *, max_iter: int=50) → float`

Static calls (including nested helper bodies): `torch.nn.Parameter`, `torch.optim.LBFGS`, `torch.zeros`, `optimizer.zero_grad`, `torch.exp`, `F.cross_entropy`, `loss.backward`, `optimizer.step`, `float`, `targets.long`, `torch.exp(log_temperature.detach()).item`, `negative_log_likelihood`, `__import__('math').isfinite`, `apply_temperature` (additional calls in source).

#### [fit_temperature.closure](../../src/calibration.py#L51)

`closure() → torch.Tensor`

Static calls (including nested helper bodies): `optimizer.zero_grad`, `torch.exp`, `F.cross_entropy`, `loss.backward`, `targets.long`.

#### [summarize_temperature_scaling](../../src/calibration.py#L72)

`summarize_temperature_scaling(logits: torch.Tensor, targets: torch.Tensor, temperature: float) → dict[str, float]`

Static calls (including nested helper bodies): `torch.softmax`, `apply_temperature`, `float`, `negative_log_likelihood`, `expected_calibration_error`.

## [src/config.py](../../src/config.py)

Implementation module; see the linked source and module guide.

### [PreprocessConfig](../../src/config.py#L15)

Tunable parameters for Day 2 preprocessing.

Most fields here are intentionally exposed so future experiments can be done
from one place without changing preprocessing logic.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `target_spacing_xy_mm` | `float` | `1.0` |
| `target_spacing_z_mm` | `float \| None` | `None` |
| `keep_z_if_coarse` | `bool` | `True` |
| `coarse_z_threshold_mm` | `float` | `3.0` |
| `resample_order` | `int` | `1` |
| `head_threshold_hu` | `float` | `-350.0` |
| `mask_opening_iterations` | `int` | `1` |
| `mask_closing_iterations` | `int` | `2` |
| `crop_margin_mm_zyx` | `tuple[float, float, float]` | `(2.0, 10.0, 10.0)` |
| `hu_clip_min` | `float` | `-1000.0` |
| `hu_clip_max` | `float` | `1000.0` |
| `normalize_min` | `float` | `0.0` |
| `normalize_max` | `float` | `1.0` |
| `save_format` | `str` | `'nii.gz'` |

### [SegmentationConfig](../../src/config.py#L54)

Tunable parameters for Day 3 classical segmentation baseline.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `bone_threshold_hu` | `float` | `-100.0` |
| `bone_opening_iterations` | `int` | `1` |
| `bone_closing_iterations` | `int` | `1` |
| `bone_min_component_voxels` | `int` | `32` |
| `bone_keep_largest_component` | `bool` | `True` |
| `brain_window_center` | `float` | `40.0` |
| `brain_window_width` | `float` | `120.0` |
| `brain_window_norm_min` | `float` | `0.05` |
| `brain_window_norm_max` | `float` | `0.95` |
| `brain_head_threshold_hu` | `float` | `-10.0` |
| `brain_opening_iterations` | `int` | `0` |
| `brain_closing_iterations` | `int` | `2` |
| `brain_fill_holes` | `bool` | `True` |
| `brain_min_component_voxels` | `int` | `256` |
| `brain_keep_largest_component` | `bool` | `True` |
| `overlay_max_slices` | `int \| None` | `None` |
| `overlay_min_representative_slices` | `int` | `20` |

### [AppConfig](../../src/config.py#L91)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `series_dir` | `Path` | `required / supplied by caller` |
| `output_dir` | `Path` | `required / supplied by caller` |
| `processed_dir` | `Path` | `required / supplied by caller` |
| `preprocess` | `PreprocessConfig` | `required / supplied by caller` |
| `segmentation` | `SegmentationConfig` | `required / supplied by caller` |

#### [_resolve_path](../../src/config.py#L99)

`_resolve_path(raw_value: str \| None, fallback: Path) → Path`

Static calls (including nested helper bodies): `fallback.resolve`, `Path(raw_value).expanduser().resolve`, `Path(raw_value).expanduser`, `Path`.

#### [load_app_config](../../src/config.py#L105)

`load_app_config(series_dir: str \| None=None, output_dir: str \| None=None, processed_dir: str \| None=None, preprocess: PreprocessConfig \| None=None, segmentation: SegmentationConfig \| None=None) → AppConfig`

Static calls (including nested helper bodies): `AppConfig`, `os.getenv`, `_resolve_path`, `PreprocessConfig`, `SegmentationConfig`.

## [src/data/__init__.py](../../src/data/__init__.py)

Implementation module; see the linked source and module guide.

## [src/data/ct25d_dataset.py](../../src/data/ct25d_dataset.py)

Implementation module; see the linked source and module guide.

### [CT25DCase](../../src/data/ct25d_dataset.py#L25)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `patient_id` | `str` | `required / supplied by caller` |
| `study_instance_uid` | `str` | `required / supplied by caller` |
| `series_instance_uid` | `str` | `required / supplied by caller` |
| `series_dir` | `Path` | `required / supplied by caller` |
| `volume_path` | `Path` | `required / supplied by caller` |
| `label_volume_path` | `Path` | `required / supplied by caller` |
| `slice_labels_dir` | `Path \| None` | `required / supplied by caller` |
| `spacing_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |
| `volume_shape_zyx` | `tuple[int, int, int]` | `required / supplied by caller` |
| `split_group_id` | `str` | `required / supplied by caller` |

#### [clamp_stack_indices](../../src/data/ct25d_dataset.py#L38)

`clamp_stack_indices(center_index: int, depth: int) → tuple[int, int, int]`

Static calls (including nested helper bodies): `max`, `min`, `ValueError`, `IndexError`.

Explicit raised conditions: `IndexError`, `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [build_25d_stack](../../src/data/ct25d_dataset.py#L49)

`build_25d_stack(volume: np.ndarray, center_index: int) → np.ndarray`

Static calls (including nested helper bodies): `clamp_stack_indices`, `np.stack`, `stack.astype`, `int`.

#### [_stable_identifier](../../src/data/ct25d_dataset.py#L62)

`_stable_identifier(raw_value: object, fallback: str) → str`

Static calls (including nested helper bodies): `str(raw_value).strip`, `str`.

#### [_read_series_identifiers](../../src/data/ct25d_dataset.py#L67)

`_read_series_identifiers(series_dir: str \| Path) → dict[str, str]`

Static calls (including nested helper bodies): `Path(series_dir).expanduser().resolve`, `sorted`, `pydicom.dcmread`, `_stable_identifier`, `FileNotFoundError`, `str`, `dataset.get`, `Path(series_dir).expanduser`, `series_path.iterdir`, `path.is_file`, `Path`.

Explicit raised conditions: `FileNotFoundError`. See source for triggers; called validators may raise additional exceptions.

#### [_resolve_volume_path](../../src/data/ct25d_dataset.py#L84)

`_resolve_volume_path(processed_dir: Path) → Path`

Static calls (including nested helper bodies): `FileNotFoundError`, `candidate.exists`, `candidate.resolve`.

Explicit raised conditions: `FileNotFoundError`. See source for triggers; called validators may raise additional exceptions.

#### [discover_legacy_case](../../src/data/ct25d_dataset.py#L94)

`discover_legacy_case(series_dir: str \| Path, processed_dir: str \| Path, label_volume_name: str='pseudo_labels_3d.npz') → CT25DCase`

Static calls (including nested helper bodies): `Path(series_dir).expanduser().resolve`, `Path(processed_dir).expanduser().resolve`, `_resolve_volume_path`, `(processed_path / 'pseudo_labels' / label_volume_name).resolve`, `load_processed_volume`, `_read_series_identifiers`, `CT25DCase`, `label_volume_path.exists`, `FileNotFoundError`, `np.load`, `tuple`, `ValueError`, `Path(series_dir).expanduser`, `Path(processed_dir).expanduser` (additional calls in source).

Explicit raised conditions: `FileNotFoundError`, `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [assign_group_splits](../../src/data/ct25d_dataset.py#L133)

`assign_group_splits(group_ids: list[str], train_ratio: float=0.7, val_ratio: float=0.15, test_ratio: float=0.15, seed: int=13) → dict[str, str]`

Static calls (including nested helper bodies): `list`, `np.asarray`, `np.any`, `np.random.default_rng`, `rng.shuffle`, `np.floor(desired).astype`, `max`, `np.maximum`, `zip`, `dict.fromkeys`, `ValueError`, `float`, `int`, `len` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [assign_single_case_slice_splits](../../src/data/ct25d_dataset.py#L192)

`assign_single_case_slice_splits(depth: int, *, val_ratio: float=0.15, test_ratio: float=0.15, context_radius: int=1) → list[str]`

Static calls (including nested helper bodies): `assert_split_support`, `ValueError`, `max`, `min`, `round`, `bool`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [assert_split_support](../../src/data/ct25d_dataset.py#L218)

`assert_split_support(assignments: list[str], radius: int=1) → None`

Static calls (including nested helper bodies): `enumerate`, `set`, `supports[name].update`, `ValueError`, `max`, `min`, `range`, `len`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [build_case_index](../../src/data/ct25d_dataset.py#L230)

`build_case_index(cases: list[CT25DCase], group_split_map: dict[str, str], slice_split_overrides: dict[str, list[str]] \| None=None) → pd.DataFrame`

Static calls (including nested helper bodies): `pd.DataFrame.from_records`, `slice_split_overrides.get`, `group_split_map.get`, `range`, `ValueError`, `clamp_stack_indices`, `records.append`, `dataframe.sort_values`, `candidate.exists`, `str`, `int`, `float`, `candidate.resolve`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [summarize_index](../../src/data/ct25d_dataset.py#L285)

`summarize_index(index_df: pd.DataFrame) → dict[str, Any]`

Static calls (including nested helper bodies): `index_df.groupby`, `int`, `str`, `len`, `index_df['patient_id'].nunique`, `index_df['series_instance_uid'].nunique`, `split_frame['patient_id'].nunique`, `split_frame['series_instance_uid'].nunique`.

### [Compose25D](../../src/data/ct25d_dataset.py#L302)

Class contract is defined by the fields and methods below.

#### [Compose25D.__init__](../../src/data/ct25d_dataset.py#L303)

`__init__(self, transforms: list[Any]) → None`

Static calls (including nested helper bodies): `list`.

#### [Compose25D.__call__](../../src/data/ct25d_dataset.py#L306)

`__call__(self, image: np.ndarray, mask: np.ndarray, rng: np.random.Generator) → tuple[np.ndarray, np.ndarray]`

Static calls (including nested helper bodies): `transform`.

### [RandomFlip25D](../../src/data/ct25d_dataset.py#L317)

Class contract is defined by the fields and methods below.

#### [RandomFlip25D.__init__](../../src/data/ct25d_dataset.py#L318)

`__init__(self, horizontal_prob: float=0.5, vertical_prob: float=0.5) → None`

Static calls (including nested helper bodies): `float`.

#### [RandomFlip25D.__call__](../../src/data/ct25d_dataset.py#L326)

`__call__(self, image: np.ndarray, mask: np.ndarray, rng: np.random.Generator) → tuple[np.ndarray, np.ndarray]`

Static calls (including nested helper bodies): `rng.random`, `np.flip(image, axis=2).copy`, `np.flip(mask, axis=1).copy`, `np.flip(image, axis=1).copy`, `np.flip(mask, axis=0).copy`, `np.flip`.

### [RandomRotate25D](../../src/data/ct25d_dataset.py#L341)

Class contract is defined by the fields and methods below.

#### [RandomRotate25D.__init__](../../src/data/ct25d_dataset.py#L342)

`__init__(self, max_degrees: float=7.5, probability: float=0.5) → None`

Static calls (including nested helper bodies): `float`.

#### [RandomRotate25D.__call__](../../src/data/ct25d_dataset.py#L350)

`__call__(self, image: np.ndarray, mask: np.ndarray, rng: np.random.Generator) → tuple[np.ndarray, np.ndarray]`

Static calls (including nested helper bodies): `float`, `ndimage.rotate`, `rng.uniform`, `rotated_image.astype`, `rotated_mask.astype`, `rng.random`.

### [RandomIntensityJitter25D](../../src/data/ct25d_dataset.py#L380)

Class contract is defined by the fields and methods below.

#### [RandomIntensityJitter25D.__init__](../../src/data/ct25d_dataset.py#L381)

`__init__(self, probability: float=0.5, scale_range: tuple[float, float]=(0.95, 1.05), shift_range: tuple[float, float]=(-0.03, 0.03), clip_range: tuple[float, float]=(0.0, 1.0)) → None`

Static calls (including nested helper bodies): `float`.

#### [RandomIntensityJitter25D.__call__](../../src/data/ct25d_dataset.py#L393)

`__call__(self, image: np.ndarray, mask: np.ndarray, rng: np.random.Generator) → tuple[np.ndarray, np.ndarray]`

Static calls (including nested helper bodies): `float`, `np.clip`, `rng.random`, `rng.uniform`, `jittered.astype`.

#### [build_default_train_transforms](../../src/data/ct25d_dataset.py#L409)

`build_default_train_transforms(rotation_degrees: float=7.5, enable_intensity_jitter: bool=True) → Compose25D`

Static calls (including nested helper bodies): `Compose25D`, `RandomFlip25D`, `RandomRotate25D`, `transforms.append`, `RandomIntensityJitter25D`.

#### [_torch_required](../../src/data/ct25d_dataset.py#L422)

`_torch_required() → None`

Static calls (including nested helper bodies): `RuntimeError`.

Explicit raised conditions: `RuntimeError`. See source for triggers; called validators may raise additional exceptions.

### [CT25DDataset](../../src/data/ct25d_dataset.py#L427)

Class contract is defined by the fields and methods below.

#### [CT25DDataset.__init__](../../src/data/ct25d_dataset.py#L428)

`__init__(self, index_csv_path: str \| Path, split: str \| None=None, label_key: str='pseudo_labels', transforms: Any \| None=None, seed: int=13, data_root: str \| Path \| None=None) → None`

Static calls (including nested helper bodies): `_torch_required`, `Path(index_csv_path).expanduser().resolve`, `pd.read_csv`, `self.index_df.duplicated(['series_instance_uid', 'slice_index']).any`, `self.index_df.groupby`, `manifest_path.exists`, `self.index_csv_path.with_suffix`, `self.index_df.iterrows`, `int`, `set`, `ValueError`, `pd.to_numeric(self.index_df[column], errors='raise').to_numpy`, `set(self.index_df['split']).issubset`, `json.loads` (additional calls in source).

Explicit raised conditions: `FileNotFoundError`, `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [CT25DDataset.__len__](../../src/data/ct25d_dataset.py#L504)

`__len__(self) → int`

Static calls (including nested helper bodies): `int`, `len`.

#### [CT25DDataset.set_epoch](../../src/data/ct25d_dataset.py#L507)

`set_epoch(self, epoch: int) → None`

Static calls (including nested helper bodies): `int`.

#### [CT25DDataset._sample_seed](../../src/data/ct25d_dataset.py#L510)

`_sample_seed(self, row: pd.Series) → int`

Static calls (including nested helper bodies): `'\|'.join`, `hashlib.sha256(raw.encode('utf-8')).hexdigest`, `int`, `str`, `hashlib.sha256`, `raw.encode`.

#### [CT25DDataset._load_volume](../../src/data/ct25d_dataset.py#L523)

`_load_volume(self, path_value: str) → np.ndarray`

Static calls (including nested helper bodies): `load_processed_volume`, `volume.astype`.

#### [CT25DDataset._load_label_volume](../../src/data/ct25d_dataset.py#L529)

`_load_label_volume(self, path_value: str) → np.ndarray`

Static calls (including nested helper bodies): `np.load`, `labels.astype`, `Path(path_value).expanduser().resolve`, `np.iscomplexobj`, `np.any`, `ValueError`, `np.issubdtype`, `np.isfinite(labels).all`, `Path(path_value).expanduser`, `np.floor`, `np.isfinite`, `Path`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [CT25DDataset.__getitem__](../../src/data/ct25d_dataset.py#L548)

`__getitem__(self, index: int) → dict[str, Any]`

Static calls (including nested helper bodies): `self._load_volume`, `self._load_label_volume`, `int`, `build_25d_stack`, `labels[slice_index].astype`, `torch.from_numpy`, `str`, `ValueError`, `np.random.default_rng`, `self.transforms`, `np.ascontiguousarray`, `tuple`, `np.isfinite(volume).all`, `labels.min` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_seed_worker](../../src/data/ct25d_dataset.py#L577)

`_seed_worker(worker_id: int) → None`

Static calls (including nested helper bodies): `np.random.seed`, `torch.initial_seed`.

#### [create_dataloaders](../../src/data/ct25d_dataset.py#L582)

`create_dataloaders(index_csv_path: str \| Path, batch_size: int=4, num_workers: int=0, seed: int=13, train_transforms: Any \| None=None, eval_transforms: Any \| None=None, shuffle_train: bool=True) → dict[str, DataLoader]`

Static calls (including nested helper bodies): `_torch_required`, `CT25DDataset`, `torch.Generator`, `generator.manual_seed`, `bool`, `DataLoader`, `int`, `len`.

## [src/dicom_loader.py](../../src/dicom_loader.py)

Implementation module; see the linked source and module guide.

### [SeriesMetadata](../../src/dicom_loader.py#L10)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `series_instance_uid` | `str` | `required / supplied by caller` |
| `modality` | `str` | `required / supplied by caller` |
| `slice_count` | `int` | `required / supplied by caller` |
| `rows` | `int` | `required / supplied by caller` |
| `columns` | `int` | `required / supplied by caller` |
| `spacing_zyx` | `tuple` | `required / supplied by caller` |
| `orientation_lps` | `tuple` | `required / supplied by caller` |
| `rescale_slope_range` | `tuple` | `required / supplied by caller` |
| `rescale_intercept_range` | `tuple` | `required / supplied by caller` |
| `z_positions` | `list` | `required / supplied by caller` |
| `validation_messages` | `list` | `required / supplied by caller` |
| `origin_lps` | `tuple` | `required / supplied by caller` |
| `direction_lps` | `tuple` | `required / supplied by caller` |
| `padding_voxels` | `int` | `required / supplied by caller` |
| `intensity_hu_range` | `tuple` | `required / supplied by caller` |

#### [SeriesMetadata.to_dict](../../src/dicom_loader.py#L27)

`to_dict(self)`

Static calls (including nested helper bodies): `asdict`, `result.pop`, `validate_public_metadata`.

### [DicomVolume](../../src/dicom_loader.py#L40)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `volume_hu` | `np.ndarray` | `required / supplied by caller` |
| `metadata` | `SeriesMetadata` | `required / supplied by caller` |

#### [_decode_with_simpleitk](../../src/dicom_loader.py#L45)

`_decode_with_simpleitk(path)`

Static calls (including nested helper bodies): `sitk.GetArrayFromImage`, `arr[0].astype`, `sitk.ReadImage`, `ValueError`, `str`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_decode_pixels](../../src/dicom_loader.py#L54)

`_decode_pixels(dataset, path)`

Static calls (including nested helper bodies): `dataset.pixel_array.astype`, `float`, `_decode_with_simpleitk`.

#### [load_dicom_series](../../src/dicom_loader.py#L64)

`load_dicom_series(series_dir, *, max_voxels=64 * 1024 * 1024)`

Static calls (including nested helper bodies): `Path(series_dir).expanduser().resolve`, `sorted`, `records.sort`, `np.array`, `np.diff`, `len`, `np.cross`, `np.concatenate`, `np.column_stack`, `SeriesMetadata`, `DicomVolume`, `ValueError`, `path.is_dir`, `FileNotFoundError` (additional calls in source).

Explicit raised conditions: `FileNotFoundError`, `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [write_metadata_json](../../src/dicom_loader.py#L218)

`write_metadata_json(metadata, output_path)`

Static calls (including nested helper bodies): `Path`, `destination.parent.mkdir`, `destination.write_text`, `json.dumps`, `metadata.to_dict`.

## [src/evaluation.py](../../src/evaluation.py)

Implementation module; see the linked source and module guide.

#### [apply_day6_postprocess](../../src/evaluation.py#L6)

`apply_day6_postprocess(probabilities_bchw: np.ndarray, *, brain_min_voxels: int=256, bone_min_voxels: int=96, overlap_min_voxels: int=32, smooth_iterations: int=1) → np.ndarray`

Static calls (including nested helper bodies): `probabilities_bchw.argmax(axis=1).astype`, `probabilities_bchw.argmax`, `postprocess_multiclass_prediction`, `np.transpose`, `LabelPostprocessConfig`, `int`.

## [src/lung_nodule/__init__.py](../../src/lung_nodule/__init__.py)

Local, source-linked lung nodule research tools. No diagnostic claims.

## [src/lung_nodule/cli.py](../../src/lung_nodule/cli.py)

Command-line entry points. Inference never downloads or automatically approves.

#### [main](../../src/lung_nodule/cli.py#L13)

`main(argv=None)`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_subparsers`, `sub.add_parser`, `fetch.add_argument`, `keygen.add_argument`, `demo.add_argument`, `detect.add_argument`, `review.add_argument`, `export.add_argument`, `research.add_argument`, `p.parse_args`, `command.add_argument`, `print`, `json.dumps` (additional calls in source).

## [src/lung_nodule/contracts.py](../../src/lung_nodule/contracts.py)

Versioned immutable-by-convention records; all persisted data is revalidated.

### [Record](../../src/lung_nodule/contracts.py#L24)

Class contract is defined by the fields and methods below.

#### [digest](../../src/lung_nodule/contracts.py#L28)

`digest(value) → str`

Canonical content identity; consistency check, not source authenticity.

Static calls (including nested helper bodies): `isinstance`, `value.model_dump`, `hashlib.sha256`, `json.dumps`.

### [Geometry](../../src/lung_nodule/contracts.py#L39)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `shape_zyx` | `tuple[StrictInt, StrictInt, StrictInt]` | `required / supplied by caller` |
| `spacing_zyx_mm` | `tuple[float, float, float]` | `required / supplied by caller` |
| `origin_lps_mm` | `tuple[float, float, float]` | `required / supplied by caller` |
| `direction_lps` | `tuple[float, ...]` | `required / supplied by caller` |

#### [Geometry.valid_geometry](../../src/lung_nodule/contracts.py#L46)

`valid_geometry(self)`

Static calls (including nested helper bodies): `model_validator`, `np.array(self.direction_lps).reshape`, `ValueError`, `min`, `max`, `np.prod`, `len`, `np.array`, `np.allclose`, `np.isclose`, `np.eye`, `np.linalg.det`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [Geometry.to_lps](../../src/lung_nodule/contracts.py#L62)

`to_lps(self, points_zyx)`

Map source voxel centers to physical LPS millimetres, including obliquity.

Static calls (including nested helper bodies): `np.asarray`, `np.array(self.direction_lps).reshape`, `np.array`.

#### [Geometry.from_lps](../../src/lung_nodule/contracts.py#L69)

`from_lps(self, points_lps)`

Static calls (including nested helper bodies): `np.array(self.direction_lps).reshape`, `np.asarray`, `np.array`.

### [SourceSlice](../../src/lung_nodule/contracts.py#L76)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `index` | `Annotated[StrictInt, Field(ge=0)]` | `required / supplied by caller` |
| `sha256` | `Digest` | `required / supplied by caller` |
| `sop_uid_sha256` | `Digest` | `required / supplied by caller` |

### [Candidate](../../src/lung_nodule/contracts.py#L82)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `candidate_id` | `Identifier` | `required / supplied by caller` |
| `box_zyx` | `tuple[float, float, float, float, float, float]` | `required / supplied by caller` |
| `score` | `Annotated[float, Field(ge=0, le=1)]` | `required / supplied by caller` |
| `kind` | `Literal['model_candidate']` | `'model_candidate'` |

#### [Candidate.ordered_box](../../src/lung_nodule/contracts.py#L89)

`ordered_box(self)`

Static calls (including nested helper bodies): `model_validator`, `np.any`, `ValueError`, `np.array`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [ModelProvenance](../../src/lung_nodule/contracts.py#L95)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `name` | `str` | `required / supplied by caller` |
| `checkpoint_sha256` | `Digest` | `required / supplied by caller` |
| `config_sha256` | `Digest` | `required / supplied by caller` |
| `execution_device` | `str` | `required / supplied by caller` |
| `software_versions` | `dict[str, str]` | `required / supplied by caller` |
| `synthetic_fixture` | `StrictBool` | `required / supplied by caller` |
| `score_threshold` | `Annotated[float, Field(ge=0, le=1)]` | `required / supplied by caller` |

### [Study](../../src/lung_nodule/contracts.py#L105)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `schema_version` | `Literal['lung-nodule-study-v1']` | `'lung-nodule-study-v1'` |
| `study_id` | `Identifier` | `required / supplied by caller` |
| `patient_alias` | `Identifier` | `required / supplied by caller` |
| `input_kind` | `Literal['generated-synthetic', 'approved-public-research']` | `required / supplied by caller` |
| `acquisition_date` | `None` | `None` |
| `source_sha256` | `Digest` | `required / supplied by caller` |
| `geometry` | `Geometry` | `required / supplied by caller` |
| `sources` | `Annotated[list[SourceSlice], Field(min_length=2, max_length=512)]` | `required / supplied by caller` |
| `model` | `ModelProvenance` | `required / supplied by caller` |
| `candidates` | `Annotated[list[Candidate], Field(max_length=300)]` | `required / supplied by caller` |
| `protocol_attestation` | `Literal['synthetic-phantom', 'adult-noncontrast-chest-complete', 'public-chest-protocol-unverified']` | `required / supplied by caller` |

#### [Study.consistent](../../src/lung_nodule/contracts.py#L123)

`consistent(self)`

Static calls (including nested helper bodies): `model_validator`, `ValueError`, `len`, `digest`, `list`, `set`, `np.any`, `range`, `self.geometry.model_dump`, `min`, `s.model_dump`, `np.array`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [Caliper](../../src/lung_nodule/contracts.py#L158)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `start_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |
| `end_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |

#### [Caliper.length_mm](../../src/lung_nodule/contracts.py#L162)

`length_mm(self, geometry)`

Static calls (including nested helper bodies): `np.array`, `float`, `np.any`, `ValueError`, `np.linalg.norm`, `np.isclose`, `int`, `np.diff`, `geometry.to_lps`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [Decision](../../src/lung_nodule/contracts.py#L177)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `candidate_id` | `Identifier` | `required / supplied by caller` |
| `decision` | `Literal['accept', 'reject', 'uncertain']` | `required / supplied by caller` |
| `caliper` | `Caliper \| None` | `None` |

### [Review](../../src/lung_nodule/contracts.py#L183)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `schema_version` | `Literal['lung-nodule-review-v1']` | `'lung-nodule-review-v1'` |
| `study_digest` | `Digest` | `required / supplied by caller` |
| `reviewer` | `Annotated[str, Field(min_length=1, max_length=100, pattern='^[^\\r\\n]+$')]` | `required / supplied by caller` |
| `qualified_reviewer_attestation` | `Literal[True]` | `required / supplied by caller` |
| `decisions` | `list[Decision]` | `required / supplied by caller` |
| `approved` | `Literal[True]` | `required / supplied by caller` |

#### [Review.literal_booleans](../../src/lung_nodule/contracts.py#L193)

`literal_booleans(cls, value)`

Static calls (including nested helper bodies): `model_validator`, `isinstance`, `any`, `ValueError`, `value.get`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [Review.verify](../../src/lung_nodule/contracts.py#L203)

`verify(self, study)`

Static calls (including nested helper bodies): `any`, `digest`, `ValueError`, `sorted`, `decision.caliper.length_mm`, `next`, `np.array`, `np.any`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [research_report](../../src/lung_nodule/contracts.py#L235)

`research_report(study, review)`

Compose only approved, structured observations; no LLM or cancer inference.

Static calls (including nested helper bodies): `review.verify`, `'\n'.join`, `study.geometry.to_lps`, `range`, `np.array`, `int`, `lines.append`, `html.escape`, `len`, `np.floor`, `digest`, `np.ceil`, `decision.caliper.length_mm`.

## [src/lung_nodule/detection.py](../../src/lung_nodule/detection.py)

Offline MONAI RetinaNet inference with explicit source/world coordinate mapping.

Network topology follows the Apache-2.0 MONAI lung_nodule_ct_detection bundle.
Upstream config is stored as provenance, never evaluated as executable Python.
Adapted topology: Copyright (c) MONAI Consortium; Apache License 2.0, see
THIRD_PARTY_NOTICES.md and third_party/MONAI-APACHE-2.0.txt.

#### [fetch_model](../../src/lung_nodule/detection.py#L53)

`fetch_model(destination)`

Explicit setup-only download from a fixed official revision; never on inference.

Static calls (including nested helper bodies): `Path(destination).resolve`, `destination.mkdir`, `(destination / 'registration.json').write_text`, `path.parent.mkdir`, `sha256`, `digest`, `json.dumps`, `Path`, `urllib.request.urlopen`, `path.open`, `source.read`, `output.write`.

#### [verify_model](../../src/lung_nodule/detection.py#L83)

`verify_model(directory)`

Reject missing/altered files before deserializing tensor-only weights.

Static calls (including nested helper bodies): `Path`, `json.loads`, `any`, `(directory / 'registration.json').read_text`, `ValueError`, `registration.get`, `digest`, `set`, `sha256`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [select_device](../../src/lung_nodule/detection.py#L105)

`select_device(requested)`

No AUTO or silent accelerator fallback. Intel NPU is not CUDA.

Static calls (including nested helper bodies): `ValueError`, `torch.device`, `torch.cuda.is_available`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [build_detector](../../src/lung_nodule/detection.py#L118)

`build_detector(device='cpu', *, score_threshold=0.15)`

Construct upstream-compatible detector without downloading weights.

Static calls (including nested helper bodies): `select_device`, `resnet50`, `resnet_fpn_feature_extractor`, `AnchorGeneratorWithAnchorShape`, `RetinaNetDetector`, `detector.set_target_keys`, `detector.set_box_selector_parameters`, `detector.set_sliding_window_inferer`, `RetinaNet`.

#### [prepare_tensor](../../src/lung_nodule/detection.py#L172)

`prepare_tensor(hu, geometry)`

Source zyx HU -> RAS xyz MetaTensor, spacing and window from upstream recipe.

Static calls (including nested helper bodies): `np.prod`, `np.eye`, `MetaTensor`, `Compose`, `transform`, `ValueError`, `np.array(geometry.direction_lps).reshape`, `np.diag`, `torch.from_numpy`, `np.ceil`, `np.ascontiguousarray`, `Orientation`, `Spacing`, `ScaleIntensityRange` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [map_boxes](../../src/lung_nodule/detection.py#L208)

`map_boxes(boxes_xyz, scores, affine_ras, geometry, threshold)`

Map all eight box corners; never flip only centers or assume axial source.

Static calls (including nested helper bodies): `zip`, `np.asarray`, `np.any`, `ValueError`, `np.array`, `geometry.from_lps`, `np.maximum`, `np.minimum`, `np.all`, `np.isfinite(boxes).all`, `np.isfinite(scores).all`, `list`, `source.min`, `source.max` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [MonaiDetector](../../src/lung_nodule/detection.py#L242)

Local pretrained 3D detector; output scores are not malignancy probabilities.

#### [MonaiDetector.__init__](../../src/lung_nodule/detection.py#L245)

`__init__(self, model_dir, *, device='cpu', threshold=0.15, checkpoint=None)`

Static calls (including nested helper bodies): `verify_model`, `build_detector`, `torch.load`, `weights.get`, `self.detector.network.load_state_dict`, `self.detector.eval`, `ModelProvenance`, `ValueError`, `select_device`, `Path`, `sha256`, `digest`, `str`, `importlib.metadata.version`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [MonaiDetector.predict](../../src/lung_nodule/detection.py#L274)

`predict(self, hu, geometry)`

Static calls (including nested helper bodies): `prepare_tensor`, `map_boxes`, `torch.inference_mode`, `output['box'].detach().cpu().numpy`, `output['label_scores'].detach().cpu().numpy`, `image.affine.cpu().numpy`, `self.detector`, `output['box'].detach().cpu`, `output['label_scores'].detach().cpu`, `image.affine.cpu`, `image.to`, `bool`, `np.any`, `output['box'].detach` (additional calls in source).

### [PhantomDetector](../../src/lung_nodule/detection.py#L295)

Deterministic sphere-fixture finder, NOT a trained lung nodule model.

#### [PhantomDetector.predict](../../src/lung_nodule/detection.py#L308)

`predict(self, hu, geometry)`

Static calls (including nested helper bodies): `label`, `range`, `ValueError`, `np.argwhere`, `np.all`, `candidates.append`, `len`, `Candidate`, `points.max`, `points.min`, `tuple`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [detect_study](../../src/lung_nodule/detection.py#L334)

`detect_study(series, detector, *, study_id, patient_alias, approval=None, inference_region=None)`

Static calls (including nested helper bodies): `load_sources`, `Study`, `ValueError`, `detector.predict`, `np.asarray`, `Geometry.model_validate`, `provenance.model_copy`, `np.any`, `dict`, `c.model_copy`, `np.issubdtype`, `geometry.model_dump`, `np.array`, `tuple` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/lung_nodule/exchange_contract.py](../../src/lung_nodule/exchange_contract.py)

Shared, ML-free MHCRA nodule exchange v2 validation and pixel rendering.

Vendored by MHCRA with only the contracts import rewritten; CI checks equality.
Hashes bind artifacts but do not authenticate producer execution or synthetic origin.

#### [byte_digest](../../src/lung_nodule/exchange_contract.py#L38)

`byte_digest(payload)`

Static calls (including nested helper bodies): `hashlib.sha256(payload).hexdigest`, `hashlib.sha256`.

### [ExchangeArtifact](../../src/lung_nodule/exchange_contract.py#L42)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `path` | `str` | `required / supplied by caller` |
| `role` | `Literal['source_volume', 'source_preview', 'overlay_preview', 'producer_report']` | `required / supplied by caller` |
| `sha256` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `size_bytes` | `int` | `Field(gt=0, le=32 * 1024 ** 2, strict=True)` |
| `slice_index` | `int \| None` | `Field(default=None, ge=0, le=63, strict=True)` |

#### [ExchangeArtifact.safe_path](../../src/lung_nodule/exchange_contract.py#L53)

`safe_path(cls, value)`

Static calls (including nested helper bodies): `field_validator`, `PurePosixPath(value).is_absolute`, `any`, `ValueError`, `len`, `PurePosixPath`, `value.split`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [PublicResearchSource](../../src/lung_nodule/exchange_contract.py#L68)

Operator-declared public provenance, never a real patient-history link.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `dataset` | `str` | `Field(min_length=1, max_length=200)` |
| `source_url` | `str` | `Field(min_length=10, max_length=500, pattern='^https://')` |
| `license` | `str` | `Field(min_length=1, max_length=300)` |
| `research_subject_id` | `str` | `Field(min_length=1, max_length=100)` |
| `original_sha256` | `str` | `Field(pattern='^[a-f0-9]{64}$')` |
| `composite_case` | `Literal[True]` | `required / supplied by caller` |

#### [PublicResearchSource.explicit_composite](../../src/lung_nodule/exchange_contract.py#L80)

`explicit_composite(cls, value)`

Static calls (including nested helper bodies): `field_validator`, `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [NoduleBundle](../../src/lung_nodule/exchange_contract.py#L88)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `schema_version` | `Literal['mhcra-lung-nodules-v2', 'lovisa-ct-research-v3']` | `required / supplied by caller` |
| `synthetic` | `bool` | `Field(strict=True)` |
| `research` | `PublicResearchSource \| None` | `None` |
| `original_study` | `Study \| None` | `None` |
| `crop_origin_zyx` | `tuple[int, int, int] \| None` | `None` |
| `inference_region_zyx` | `tuple[int, int, int, int, int, int] \| None` | `None` |
| `patient_id` | `Identifier` | `required / supplied by caller` |
| `study_id` | `Identifier` | `required / supplied by caller` |
| `job_id` | `str` | `Field(pattern='^[a-f0-9]{32}$')` |
| `acquisition_date` | `None` | `required / supplied by caller` |
| `processed_at` | `datetime` | `required / supplied by caller` |
| `status` | `Literal['pending_review', 'producer_reviewed']` | `required / supplied by caller` |
| `study` | `Study` | `required / supplied by caller` |
| `producer_review` | `Review \| None` | `required / supplied by caller` |
| `artifacts` | `list[ExchangeArtifact]` | `Field(min_length=6, max_length=130)` |

#### [NoduleBundle.consistent](../../src/lung_nodule/exchange_contract.py#L106)

`consistent(self)`

Static calls (including nested helper bodies): `model_validator`, `self.verify_research_crop`, `ValueError`, `self.producer_review.verify`, `any`, `len`, `a.path.endswith`, `range`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [NoduleBundle.verify_research_crop](../../src/lung_nodule/exchange_contract.py#L165)

`verify_research_crop(self)`

Bind a limited HU excerpt to exact original geometry and candidate coordinates.

Whole-source hashes record provenance; they do not authenticate a producer.
The consumer independently checks excerpt pixels/previews, not absent full scans.

Static calls (including nested helper bodies): `original.geometry.model_dump`, `geometry.update`, `np.array`, `ValueError`, `np.any`, `any`, `Geometry.model_validate`, `SourceSlice.model_validate`, `self.patient_id.startswith`, `min`, `tuple`, `dict`, `enumerate`, `np.all` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [wire_pixels](../../src/lung_nodule/exchange_contract.py#L240)

`wire_pixels(study, hu, index, *, calipers=())`

Portable NumPy-only source/box/caliper pixels; no font-version dependency.

Static calls (including nested helper bodies): `(np.clip((hu[index] + 1000) / 1400, 0, 1) * 255).astype`, `np.repeat`, `source.copy`, `ValueError`, `c.length_mm`, `np.array`, `np.floor(lo[1:]).astype`, `np.ceil(hi[1:]).astype`, `np.rint(np.linspace(a, b, count)).astype`, `np.clip`, `int`, `np.floor`, `np.ceil`, `math.ceil` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [source_pixels](../../src/lung_nodule/exchange_contract.py#L266)

`source_pixels(bundle, artifacts)`

Bound NPY header and exact payload before allocating source HU.

Static calls (including nested helper bodies): `next`, `io.BytesIO`, `np.lib.format.read_magic`, `readers[version]`, `np.load`, `ValueError`, `np.isfinite(hu).all`, `np.dtype`, `len`, `handle.tell`, `math.prod`, `np.isfinite`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [unique_object](../../src/lung_nodule/exchange_contract.py#L294)

`unique_object(pairs)`

Static calls (including nested helper bodies): `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [read_exchange](../../src/lung_nodule/exchange_contract.py#L303)

`read_exchange(payload, patient_id)`

Validate bounded ZIP without extracting paths; all source/overlay pixels checked.

Static calls (including nested helper bodies): `ValueError`, `source_pixels`, `next`, `range`, `len`, `zipfile.ZipFile`, `z.infolist`, `any`, `z.read`, `NoduleBundle.model_validate`, `research_report`, `artifacts[report.path].decode`, `wire_pixels`, `io.BytesIO` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/lung_nodule/phantom.py](../../src/lung_nodule/phantom.py)

Small reproducible chest-like phantom with known spheres, never clinical validation.

#### [generate_chest](../../src/lung_nodule/phantom.py#L11)

`generate_chest(destination, *, seed=7, lesion=True)`

Generate 32x64x64 DICOM, 1.5x1x1mm spacing and optional synthetic sphere.

Static calls (including nested helper bodies): `Path`, `directory.mkdir`, `np.where`, `np.random.default_rng(seed).normal`, `range`, `directory.with_name(directory.name + '.synthetic.json').write_text`, `generate_uid`, `FileMetaDataset`, `FileDataset`, `hu[z].astype(np.int16).tobytes`, `ds.save_as`, `json.dumps`, `np.random.default_rng`, `str` (additional calls in source).

## [src/lung_nodule/producer_signature.py](../../src/lung_nodule/producer_signature.py)

Ed25519 producer signatures for LOVISA review ZIPs.

This file is copied byte-for-byte into the CT companion, the endoscopy companion
and LOVISA; keep it self-contained. A valid signature from a pinned key shows that
the holder of that private key exported these exact ``bundle.json`` bytes, which
in turn hash-bind every artifact. It does not prove model correctness, data
permission, clinical truth or the signer's qualifications. Research use only.

### [Record](../../src/lung_nodule/producer_signature.py#L30)

Class contract is defined by the fields and methods below.

### [Performance](../../src/lung_nodule/producer_signature.py#L34)

Producer-declared evaluation of the exact model; shown beside candidates.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `measured` | `bool` | `required / supplied by caller` |
| `metric` | `str` | `Field(min_length=1, max_length=200)` |
| `false_positive_fraction` | `Optional[float]` | `Field(default=None, ge=0, le=1)` |
| `test_images` | `Optional[int]` | `Field(default=None, ge=1, strict=True)` |
| `negative_images` | `Optional[int]` | `Field(default=None, ge=0, strict=True)` |
| `evaluation_sha256` | `Optional[str]` | `Field(default=None, pattern='^[a-f0-9]{64}$')` |
| `limitations` | `str` | `Field(min_length=1, max_length=600)` |

#### [Performance.complete](../../src/lung_nodule/producer_signature.py#L46)

`complete(self)`

Static calls (including nested helper bodies): `model_validator`, `any`, `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

### [Claims](../../src/lung_nodule/producer_signature.py#L62)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `schema_version` | `Literal['lovisa-producer-signature-v1']` | `required / supplied by caller` |
| `producer` | `Producer` | `required / supplied by caller` |
| `bundle_sha256` | `str` | `Hex64` |
| `key_id` | `str` | `Hex64` |
| `signed_at` | `datetime` | `required / supplied by caller` |
| `performance` | `Performance` | `required / supplied by caller` |

### [Envelope](../../src/lung_nodule/producer_signature.py#L71)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `claims` | `Claims` | `required / supplied by caller` |
| `signature_b64` | `str` | `Field(min_length=80, max_length=100)` |

### [Check](../../src/lung_nodule/producer_signature.py#L76)

Result of checking an archive against locally pinned producer keys.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `status` | `Literal['verified', 'unsigned', 'untrusted-key']` | `required / supplied by caller` |
| `producer` | `Optional[Producer]` | `None` |
| `key_id` | `Optional[str]` | `None` |
| `label` | `Optional[str]` | `None` |
| `performance` | `Optional[Performance]` | `None` |

#### [canonical](../../src/lung_nodule/producer_signature.py#L86)

`canonical(value) → bytes`

Static calls (including nested helper bodies): `isinstance`, `value.model_dump`, `json.dumps`.

#### [key_id](../../src/lung_nodule/producer_signature.py#L92)

`key_id(public_raw: bytes) → str`

Static calls (including nested helper bodies): `hashlib.sha256(public_raw).hexdigest`, `hashlib.sha256`.

#### [_crypto](../../src/lung_nodule/producer_signature.py#L96)

`_crypto()`

Static calls (including nested helper bodies): `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_public_raw](../../src/lung_nodule/producer_signature.py#L106)

`_public_raw(public_key) → bytes`

Static calls (including nested helper bodies): `_crypto`, `public_key.public_bytes`.

#### [generate_key](../../src/lung_nodule/producer_signature.py#L113)

`generate_key(path) → dict`

Create a new owner-only PKCS8 private key file; never overwrite an existing one.

Static calls (including nested helper bodies): `_crypto`, `ed25519.Ed25519PrivateKey.generate`, `private.private_bytes`, `Path`, `path.parent.mkdir`, `os.open`, `public_info`, `serialization.NoEncryption`, `os.fdopen`, `handle.write`, `private.public_key`.

#### [public_info](../../src/lung_nodule/producer_signature.py#L130)

`public_info(public_key) → dict`

Static calls (including nested helper bodies): `_public_raw`, `key_id`, `base64.b64encode(raw).decode`, `base64.b64encode`.

#### [load_private_key](../../src/lung_nodule/producer_signature.py#L135)

`load_private_key(path)`

Static calls (including nested helper bodies): `_crypto`, `Path`, `serialization.load_pem_private_key`, `ValueError`, `path.read_bytes`, `isinstance`, `stat.S_IMODE`, `path.stat`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [sign_archive](../../src/lung_nodule/producer_signature.py#L146)

`sign_archive(payload: bytes, private_key, producer, performance=NOT_MEASURED) → bytes`

Return the same archive with an added signature over bundle.json and claims.

Static calls (including nested helper bodies): `Claims`, `Envelope`, `io.BytesIO`, `stream.getvalue`, `zipfile.ZipFile`, `archive.infolist`, `dict`, `archive.writestr`, `archive.namelist`, `ValueError`, `entries.append`, `hashlib.sha256(bundle).hexdigest`, `datetime.now`, `Performance.model_validate` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_unique](../../src/lung_nodule/producer_signature.py#L175)

`_unique(pairs)`

Static calls (including nested helper bodies): `ValueError`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [check_archive](../../src/lung_nodule/producer_signature.py#L184)

`check_archive(payload: bytes, trusted: dict) → Check`

Check a signature against ``{key_id: {"producer", "public_key_b64", "label"}}``.

Unsigned archives and signatures from unpinned keys are reported, not trusted;
callers decide whether to accept them. A present signature that is malformed,
does not match bundle.json, names the wrong producer or fails verification
raises ValueError.

Static calls (including nested helper bodies): `_crypto`, `trusted.get`, `base64.b64decode`, `Check`, `hashlib.sha256(bundle).hexdigest`, `ValueError`, `ed25519.Ed25519PublicKey.from_public_bytes(raw).verify`, `zipfile.ZipFile`, `archive.namelist`, `archive.getinfo`, `Envelope.model_validate`, `archive.read`, `key_id`, `canonical` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/lung_nodule/research.py](../../src/lung_nodule/research.py)

Patient-separated research manifests, local GPU training and transparent FROC.

This is an engineering metric, not the official LUNA16 scorer: no challenge
excluded-nodule categories or bootstrap intervals are inferred from absent data.

### [NoduleTruth](../../src/lung_nodule/research.py#L23)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `center_lps_mm` | `tuple[float, float, float]` | `required / supplied by caller` |
| `diameter_mm` | `float` | `Field(gt=0, le=100)` |

### [DatasetCase](../../src/lung_nodule/research.py#L28)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `patient_id` | `Identifier` | `required / supplied by caller` |
| `study_id` | `Identifier` | `required / supplied by caller` |
| `split` | `str` | `Field(pattern='^(training\|validation\|test)$')` |
| `image` | `str` | `required / supplied by caller` |
| `image_sha256` | `Digest` | `required / supplied by caller` |
| `annotations_complete` | `StrictBool` | `required / supplied by caller` |
| `nodules` | `list[NoduleTruth]` | `required / supplied by caller` |

### [DatasetManifest](../../src/lung_nodule/research.py#L38)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `schema_version` | `str` | `Field(pattern='^lung-nodule-dataset-v1$')` |
| `public_research_approved` | `StrictBool` | `required / supplied by caller` |
| `approved_by` | `str` | `Field(min_length=1)` |
| `dataset` | `str` | `Field(min_length=1)` |
| `license` | `str` | `Field(min_length=1)` |
| `intensity_units` | `Literal['HU']` | `required / supplied by caller` |
| `cases` | `list[DatasetCase]` | `Field(min_length=3, max_length=10000)` |

#### [DatasetManifest.group_separation](../../src/lung_nodule/research.py#L48)

`group_separation(self)`

Static calls (including nested helper bodies): `model_validator`, `set`, `ValueError`, `studies.add`, `Path`, `path.is_absolute`, `c.image.endswith`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [validate_dataset](../../src/lung_nodule/research.py#L82)

`validate_dataset(manifest_path, dataset_root)`

Check image hashes, LPS-aware affine, HU scale declaration and model spacing.

Static calls (including nested helper bodies): `DatasetManifest.model_validate_json`, `Path(dataset_root).resolve`, `Path(manifest_path).read_bytes`, `(root / case.image).resolve`, `nib.load`, `np.asanyarray`, `Path`, `ValueError`, `np.allclose`, `np.iscomplexobj`, `np.linalg.solve`, `path.is_relative_to`, `sha256`, `len` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [prepare_training_image](../../src/lung_nodule/research.py#L123)

`prepare_training_image(series, destination, *, approval=None)`

Write HU NIfTI at upstream training spacing; no labels or split are invented.

Static calls (including nested helper bodies): `load_sources`, `Path`, `sitk.GetImageFromArray`, `image.SetSpacing`, `image.SetOrigin`, `image.SetDirection`, `sitk.Resample`, `destination.parent.mkdir`, `sitk.WriteImage`, `destination.exists`, `ValueError`, `np.prod`, `sitk.Transform`, `image.GetOrigin` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [launch_training](../../src/lung_nodule/research.py#L165)

`launch_training(*, manifest_path, dataset_root, model_dir, output, epochs=1)`

Run the pinned upstream trainer on CUDA with explicit patient-separated data.

Downloads never occur here. Test cohort is never passed to the training
subprocess. This launcher does not claim that pretrained weights were unseen
on any cohort; the dataset/model overlap audit remains a separate requirement.

Static calls (including nested helper bodies): `select_device`, `verify_model`, `validate_dataset`, `Path(output).resolve`, `output.mkdir`, `datalist.write_text`, `json.loads`, `config.update`, `config_path.write_text`, `record.write_text`, `ValueError`, `json.dumps`, `str`, `min` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [froc](../../src/lung_nodule/research.py#L252)

`froc(cases, operating_points=(0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0))`

Center-distance matching on complete volumes; duplicates count as false positives.

Input per scan: truths[{center_lps_mm,diameter_mm}], predictions[{center_lps_mm,score}].
Include genuinely negative scans in the denominator. No bootstrapped CI is claimed.

Static calls (including nested helper bodies): `sum`, `sorted`, `ValueError`, `float`, `curve.append`, `max`, `len`, `list`, `c.get`, `NoduleTruth.model_validate`, `thresholds.add`, `np.mean`, `np.linalg.norm`, `linear_sum_assignment` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [main](../../src/lung_nodule/research.py#L318)

`main(argv=None)`

Static calls (including nested helper bodies): `argparse.ArgumentParser`, `p.add_subparsers`, `sub.add_parser`, `q.add_argument`, `p.parse_args`, `validate_dataset`, `print`, `json.dumps`, `launch_training`, `froc`, `Path(a.output).write_text`, `len`, `digest`, `json.loads` (additional calls in source).

## [src/lung_nodule/sources.py](../../src/lung_nodule/sources.py)

Load immutable synthetic or explicitly approved public research sources.

#### [sha256](../../src/lung_nodule/sources.py#L16)

`sha256(path)`

Static calls (including nested helper bodies): `hashlib.sha256`, `h.hexdigest`, `Path(path).open`, `iter`, `h.update`, `Path`, `handle.read`.

#### [load_sources](../../src/lung_nodule/sources.py#L24)

`load_sources(directory, *, approval=None)`

Read one series twice-bound to byte hashes; no filenames or raw UIDs in output.

Static calls (including nested helper bodies): `Path(directory).resolve`, `directory.with_name`, `sorted`, `marker.exists`, `load_dicom_series`, `Geometry`, `digest`, `sha256`, `json.loads`, `len`, `ValueError`, `set`, `np.array(volume.metadata.direction_lps).reshape`, `pydicom.dcmread` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/lung_nodule/ui.py](../../src/lung_nodule/ui.py)

Local Streamlit review UI; launch with the documented loopback-only command.

#### [main](../../src/lung_nodule/ui.py#L16)

`main()`

Static calls (including nested helper bodies): `st.set_page_config`, `st.title`, `st.warning`, `st.caption`, `st.text_input`, `st.write`, `st.selectbox`, `st.slider`, `st.columns`, `left.image`, `right.image`, `st.code`, `st.dataframe`, `(Path(workspace) / 'review.json').exists` (additional calls in source).

## [src/lung_nodule/workspace.py](../../src/lung_nodule/workspace.py)

Local study snapshots and deterministic reports; human approval binds all content.

#### [save_workspace](../../src/lung_nodule/workspace.py#L16)

`save_workspace(destination, study, hu, *, inference_region=None)`

Create a new workspace; never overwrite a study or mutate original DICOM.

Static calls (including nested helper bodies): `Path`, `np.asarray`, `destination.mkdir`, `(destination / 'study.json').write_text`, `np.save`, `(destination / 'integrity.json').write_text`, `np.iscomplexobj`, `np.any`, `ValueError`, `study.model_dump_json`, `hu.astype`, `json.dumps`, `np.issubdtype`, `np.isfinite(hu).all` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [load_workspace](../../src/lung_nodule/workspace.py#L55)

`load_workspace(directory)`

Verify dimensions/header before array allocation and check snapshot integrity.

Static calls (including nested helper bodies): `Path`, `Study.model_validate_json`, `json.loads`, `np.load`, `ValueError`, `(directory / 'study.json').read_bytes`, `(directory / 'integrity.json').read_text`, `path.open`, `np.lib.format.read_magic`, `reader`, `np.isfinite(pixels).all`, `(directory / 'study.json').stat`, `integrity.get`, `digest` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [overlay_slice](../../src/lung_nodule/workspace.py#L90)

`overlay_slice(study, hu, z, *, annotated=True, calipers=())`

Lung-window source pixels plus source-grid candidate boxes; no altered anatomy.

Static calls (including nested helper bodies): `(np.clip((hu[z] + 1000) / 1400, 0, 1) * 255).astype`, `Image.fromarray(gray).convert`, `ImageDraw.Draw`, `ValueError`, `caliper.length_mm`, `len`, `Image.fromarray`, `draw.line`, `draw.text`, `np.clip`, `np.array`, `draw.rectangle`, `draw.ellipse`, `max`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [report_text](../../src/lung_nodule/workspace.py#L118)

`report_text(study, review)`

Use the shared deterministic CT/MHCRA report contract.

Static calls (including nested helper bodies): `research_report`.

#### [complete_review](../../src/lung_nodule/workspace.py#L125)

`complete_review(directory, review)`

Re-read source snapshot immediately before exporting a completed report.

Static calls (including nested helper bodies): `Path`, `load_workspace`, `report_text`, `(directory / 'report.md').write_text`, `(directory / 'review.json').write_text`, `review.model_dump_json`.

#### [reviewed_report](../../src/lung_nodule/workspace.py#L138)

`reviewed_report(directory)`

Recompose on every download; stale/tampered report files cannot confer approval.

Static calls (including nested helper bodies): `Path`, `load_workspace`, `Review.model_validate_json`, `report_text`, `(directory / 'review.json').read_bytes`.

#### [_export_exchange](../../src/lung_nodule/workspace.py#L146)

`_export_exchange(directory, destination, *, pending=False, research=None, original_study=None, crop_origin_zyx=None, inference_region=None, signing_key=None)`

Export verified v2 source/annotation bundle; pending mode grants no approval.

With ``signing_key`` (an Ed25519 key file path) the archive carries a producer
signature. CT performance is always declared unmeasured: no FROC or
false-positive evaluation exists for this detector.

Static calls (including nested helper bodies): `load_workspace`, `range`, `BytesIO`, `archive_bytes.getvalue`, `read_exchange`, `destination.parent.mkdir`, `Path`, `ValueError`, `review_path.exists`, `Review.model_validate_json`, `report_text`, `(directory / 'source.npy').read_bytes`, `report.encode`, `len` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [export_synthetic_exchange](../../src/lung_nodule/workspace.py#L250)

`export_synthetic_exchange(directory, destination, *, pending=False, signing_key=None)`

Legacy synthetic-v2 export; public studies require the explicit research API.

Static calls (including nested helper bodies): `_export_exchange`.

#### [export_research_exchange](../../src/lung_nodule/workspace.py#L257)

`export_research_exchange(directory, destination, *, patient_id, research, crop_origin_zyx, shape_zyx, signing_key=None)`

Export an unreviewed, bounded, source-mapped public CT excerpt to a composite case.

No resampling or inferred anatomy is introduced. Whole-source study metadata and
hashes remain in the manifest; absent scan pixels are never claimed to be covered.

Static calls (including nested helper bodies): `load_workspace`, `json.loads`, `integrity.get`, `PublicResearchSource.model_validate`, `Geometry.model_validate`, `dict`, `Study.model_validate`, `(Path(directory) / 'integrity.json').read_text`, `ValueError`, `sha256`, `np.array`, `np.any`, `SourceSlice.model_validate`, `original.model_dump` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/models/__init__.py](../../src/models/__init__.py)

Implementation module; see the linked source and module guide.

## [src/models/unet_small.py](../../src/models/unet_small.py)

Implementation module; see the linked source and module guide.

### [DoubleConv](../../src/models/unet_small.py#L10)

Class contract is defined by the fields and methods below.

#### [DoubleConv.__init__](../../src/models/unet_small.py#L11)

`__init__(self, in_channels: int, out_channels: int) → None`

Static calls (including nested helper bodies): `super().__init__`, `nn.Sequential`, `nn.Conv2d`, `nn.BatchNorm2d`, `nn.ReLU`, `super`.

#### [DoubleConv.forward](../../src/models/unet_small.py#L22)

`forward(self, x: torch.Tensor) → torch.Tensor`

Static calls (including nested helper bodies): `self.block`.

### [DownBlock](../../src/models/unet_small.py#L26)

Class contract is defined by the fields and methods below.

#### [DownBlock.__init__](../../src/models/unet_small.py#L27)

`__init__(self, in_channels: int, out_channels: int) → None`

Static calls (including nested helper bodies): `super().__init__`, `nn.MaxPool2d`, `DoubleConv`, `super`.

#### [DownBlock.forward](../../src/models/unet_small.py#L32)

`forward(self, x: torch.Tensor) → torch.Tensor`

Static calls (including nested helper bodies): `self.conv`, `self.pool`.

### [UpBlock](../../src/models/unet_small.py#L36)

Class contract is defined by the fields and methods below.

#### [UpBlock.__init__](../../src/models/unet_small.py#L37)

`__init__(self, in_channels: int, skip_channels: int, out_channels: int) → None`

Static calls (including nested helper bodies): `super().__init__`, `nn.ConvTranspose2d`, `DoubleConv`, `super`.

#### [UpBlock.forward](../../src/models/unet_small.py#L42)

`forward(self, x: torch.Tensor, skip: torch.Tensor) → torch.Tensor`

Static calls (including nested helper bodies): `self.up`, `torch.cat`, `self.conv`, `F.interpolate`.

### [UNetSmall](../../src/models/unet_small.py#L52)

Class contract is defined by the fields and methods below.

#### [UNetSmall.__init__](../../src/models/unet_small.py#L53)

`__init__(self, in_channels: int=3, num_classes: int=4, base_channels: int=16) → None`

Static calls (including nested helper bodies): `super().__init__`, `DoubleConv`, `DownBlock`, `UpBlock`, `nn.Conv2d`, `super`.

#### [UNetSmall.forward](../../src/models/unet_small.py#L69)

`forward(self, x: torch.Tensor) → torch.Tensor`

Static calls (including nested helper bodies): `self.encoder1`, `self.encoder2`, `self.encoder3`, `self.bottleneck`, `self.decoder3`, `self.decoder2`, `self.decoder1`, `self.head`.

### [MetricResult](../../src/models/unet_small.py#L81)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `dice` | `float` | `required / supplied by caller` |
| `iou` | `float` | `required / supplied by caller` |

#### [one_hot_labels](../../src/models/unet_small.py#L86)

`one_hot_labels(targets: torch.Tensor, num_classes: int) → torch.Tensor`

Static calls (including nested helper bodies): `F.one_hot`, `encoded.permute(0, 3, 1, 2).float`, `ValueError`, `targets.long`, `encoded.permute`, `tuple`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [multiclass_dice_loss](../../src/models/unet_small.py#L95)

`multiclass_dice_loss(logits: torch.Tensor, targets: torch.Tensor, num_classes: int, include_background: bool=False, smooth: float=1e-05) → torch.Tensor`

Static calls (including nested helper bodies): `torch.softmax`, `one_hot_labels(targets, num_classes=num_classes).to`, `torch.sum`, `dice.mean`, `one_hot_labels`.

#### [combined_dice_ce_loss](../../src/models/unet_small.py#L118)

`combined_dice_ce_loss(logits: torch.Tensor, targets: torch.Tensor, num_classes: int, ce_weight: float=0.5, dice_weight: float=0.5, class_weights: torch.Tensor \| None=None) → torch.Tensor`

Static calls (including nested helper bodies): `F.cross_entropy`, `multiclass_dice_loss`, `targets.long`.

#### [compute_segmentation_metrics](../../src/models/unet_small.py#L133)

`compute_segmentation_metrics(predictions: torch.Tensor, targets: torch.Tensor, num_classes: int, include_background: bool=False, smooth: float=1e-05) → dict[str, float \| dict[str, float]]`

Static calls (including nested helper bodies): `targets.long`, `predictions.argmax`, `predictions.long`, `range`, `torch.logical_and(pred_mask, target_mask).sum`, `torch.logical_or(pred_mask, target_mask).sum`, `pred_mask.sum`, `target_mask.sum`, `float`, `dice_values.append`, `iou_values.append`, `torch.stack(dice_values).mean`, `torch.tensor`, `torch.stack(iou_values).mean` (additional calls in source).

## [src/preprocessing.py](../../src/preprocessing.py)

Implementation module; see the linked source and module guide.

### [BoundingBox3D](../../src/preprocessing.py#L19)

Axis-aligned 3D bounding box using inclusive-exclusive indexing.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `z_min` | `int` | `required / supplied by caller` |
| `z_max` | `int` | `required / supplied by caller` |
| `y_min` | `int` | `required / supplied by caller` |
| `y_max` | `int` | `required / supplied by caller` |
| `x_min` | `int` | `required / supplied by caller` |
| `x_max` | `int` | `required / supplied by caller` |

#### [BoundingBox3D.as_slices](../../src/preprocessing.py#L29)

`as_slices(self) → tuple[slice, slice, slice]`

Static calls (including nested helper bodies): `slice`.

#### [BoundingBox3D.to_dict](../../src/preprocessing.py#L36)

`to_dict(self) → dict[str, int]`

### [PreprocessResult](../../src/preprocessing.py#L48)

Outputs from the day-2 preprocessing pipeline.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `resampled_volume_hu` | `np.ndarray` | `required / supplied by caller` |
| `cropped_volume_hu` | `np.ndarray` | `required / supplied by caller` |
| `processed_volume` | `np.ndarray` | `required / supplied by caller` |
| `input_spacing_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |
| `resampled_spacing_zyx` | `tuple[float, float, float]` | `required / supplied by caller` |
| `crop_bbox_zyx` | `BoundingBox3D` | `required / supplied by caller` |

#### [choose_target_spacing](../../src/preprocessing.py#L59)

`choose_target_spacing(spacing_zyx: tuple[float, float, float], preprocess_config: PreprocessConfig) → tuple[float, float, float]`

Build output spacing from config while preserving coarse z when requested.

Static calls (including nested helper bodies): `validate_spacing_zyx`, `float`.

#### [resample_volume_to_spacing](../../src/preprocessing.py#L81)

`resample_volume_to_spacing(volume_hu: np.ndarray, spacing_zyx: tuple[float, float, float], target_spacing_zyx: tuple[float, float, float], interpolation_order: int=1) → np.ndarray`

Resample a z/y/x volume to target spacing using scipy zoom.

Parameters to tune:
- `interpolation_order`: 0 keeps sharp labels, 1 is safe default for CT intensity.
- `target_spacing_zyx`: lower spacing values increase resolution and memory use.

Static calls (including nested helper bodies): `np.asarray`, `tuple`, `np.any`, `ValueError`, `np.maximum`, `ndimage.affine_transform`, `np.diag`, `np.rint`, `np.array`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_largest_connected_component](../../src/preprocessing.py#L116)

`_largest_connected_component(mask: np.ndarray) → np.ndarray`

Static calls (including nested helper bodies): `ndimage.label`, `ndimage.sum`, `ValueError`, `int`, `np.arange`, `np.argmax`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [create_head_mask](../../src/preprocessing.py#L128)

`create_head_mask(volume_hu: np.ndarray, threshold_hu: float, opening_iterations: int=1, closing_iterations: int=2) → np.ndarray`

Create a binary mask separating patient/head from surrounding air.

Parameters to tune:
- `threshold_hu`: lower values include more low-density tissue/couch.
- `opening_iterations`: removes small noise components.
- `closing_iterations`: fills small interior holes.

Static calls (including nested helper bodies): `ndimage.generate_binary_structure`, `_largest_connected_component`, `float`, `ndimage.binary_opening`, `ndimage.binary_closing`, `int`.

#### [bbox_from_mask](../../src/preprocessing.py#L157)

`bbox_from_mask(mask: np.ndarray) → BoundingBox3D`

Static calls (including nested helper bodies): `np.argwhere`, `coordinates.min`, `BoundingBox3D`, `ValueError`, `coordinates.max`, `int`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [expand_bbox_with_margin](../../src/preprocessing.py#L174)

`expand_bbox_with_margin(bbox: BoundingBox3D, margin_mm_zyx: tuple[float, float, float], spacing_zyx: tuple[float, float, float], volume_shape_zyx: tuple[int, int, int]) → BoundingBox3D`

Expand a bounding box by physical margin and clamp to volume boundaries.

Static calls (including nested helper bodies): `BoundingBox3D`, `int`, `np.rint`, `max`, `min`, `np.asarray`.

#### [crop_volume_to_bbox](../../src/preprocessing.py#L199)

`crop_volume_to_bbox(volume: np.ndarray, bbox: BoundingBox3D) → np.ndarray`

Static calls (including nested helper bodies): `volume[bbox.as_slices()].astype`, `bbox.as_slices`.

#### [clip_and_normalize_hu](../../src/preprocessing.py#L203)

`clip_and_normalize_hu(volume_hu: np.ndarray, clip_min_hu: float, clip_max_hu: float, normalize_min: float=0.0, normalize_max: float=1.0) → np.ndarray`

Clip HU to a chosen range and map to output numeric range.

Static calls (including nested helper bodies): `np.clip`, `normalized.astype`, `ValueError`, `float`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [run_preprocessing_pipeline](../../src/preprocessing.py#L223)

`run_preprocessing_pipeline(volume_hu: np.ndarray, spacing_zyx: tuple[float, float, float], preprocess_config: PreprocessConfig) → PreprocessResult`

Static calls (including nested helper bodies): `choose_target_spacing`, `validate_spacing_zyx`, `resample_volume_to_spacing`, `create_head_mask`, `bbox_from_mask`, `expand_bbox_with_margin`, `crop_volume_to_bbox`, `clip_and_normalize_hu`, `PreprocessResult`, `tuple`, `int`, `float`.

#### [_looks_like_nifti](../../src/preprocessing.py#L270)

`_looks_like_nifti(path: Path) → bool`

Static calls (including nested helper bodies): `path.name.lower`, `name.endswith`.

#### [save_npz_volume](../../src/preprocessing.py#L275)

`save_npz_volume(volume: np.ndarray, spacing_zyx: tuple[float, float, float], output_path: str \| Path) → Path`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `np.savez_compressed`, `Path(output_path).expanduser`, `volume.astype`, `np.asarray`, `Path`.

#### [load_npz_volume](../../src/preprocessing.py#L291)

`load_npz_volume(path: str \| Path) → tuple[np.ndarray, tuple[float, float, float]]`

Static calls (including nested helper bodies): `Path(path).expanduser().resolve`, `np.load`, `data['volume'].astype`, `tuple`, `Path(path).expanduser`, `float`, `Path`, `data['spacing_zyx'].tolist`.

#### [save_nifti_volume](../../src/preprocessing.py#L299)

`save_nifti_volume(volume: np.ndarray, spacing_zyx: tuple[float, float, float], output_path: str \| Path) → Path`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `sitk.GetImageFromArray`, `image.SetSpacing`, `sitk.WriteImage`, `RuntimeError`, `volume.astype`, `str`, `Path(output_path).expanduser`, `float`, `Path`.

Explicit raised conditions: `RuntimeError`. See source for triggers; called validators may raise additional exceptions.

#### [load_nifti_volume](../../src/preprocessing.py#L318)

`load_nifti_volume(path: str \| Path) → tuple[np.ndarray, tuple[float, float, float]]`

Static calls (including nested helper bodies): `sitk.ReadImage`, `image.GetSpacing`, `sitk.GetArrayFromImage(image).astype`, `RuntimeError`, `str`, `float`, `Path(path).expanduser().resolve`, `sitk.GetArrayFromImage`, `Path(path).expanduser`, `Path`.

Explicit raised conditions: `RuntimeError`. See source for triggers; called validators may raise additional exceptions.

#### [save_processed_volume](../../src/preprocessing.py#L331)

`save_processed_volume(volume: np.ndarray, spacing_zyx: tuple[float, float, float], output_path: str \| Path) → Path`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `_looks_like_nifti`, `ValueError`, `save_nifti_volume`, `output_file.suffix.lower`, `save_npz_volume`, `Path(output_path).expanduser`, `Path`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [load_processed_volume](../../src/preprocessing.py#L344)

`load_processed_volume(path: str \| Path) → tuple[np.ndarray, tuple[float, float, float]]`

Static calls (including nested helper bodies): `Path(path).expanduser().resolve`, `_looks_like_nifti`, `ValueError`, `load_nifti_volume`, `source_path.suffix.lower`, `load_npz_volume`, `Path(path).expanduser`, `Path`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [restore_prediction_to_source](../../src/preprocessing.py#L355)

`restore_prediction_to_source(prediction, result, source_shape)`

Undo model resize/crop/resample with nearest-neighbor label interpolation.

Static calls (including nested helper bodies): `np.asarray`, `np.zeros`, `ndimage.zoom`, `result.crop_bbox_zyx.as_slices`, `ndimage.affine_transform`, `np.array`, `np.diag`, `tuple`.

#### [geometry_transform](../../src/preprocessing.py#L377)

`geometry_transform(metadata, result)`

Static calls (including nested helper bodies): `np.array(metadata.direction_lps).reshape`, `np.array`, `list`, `bounds.to_dict`, `(np.array(metadata.origin_lps) + direction @ offset_xyz).tolist`.

## [src/public_metadata.py](../../src/public_metadata.py)

Allowlisted public metadata; aliasing alone is not DICOM anonymization.

#### [validate_public_metadata](../../src/public_metadata.py#L27)

`validate_public_metadata(data)`

Static calls (including nested helper bodies): `json.dumps`, `re.search`, `any`, `set`, `ValueError`, `data.get`, `min`, `re.fullmatch`, `type`, `isinstance`, `len`, `__import__('math').isfinite`, `__import__`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/robustness.py](../../src/robustness.py)

Implementation module; see the linked source and module guide.

### [LabelPostprocessConfig](../../src/robustness.py#L10)

Class contract is defined by the fields and methods below.

| Declared field | Type | Default / constraint expression |
| --- | --- | --- |
| `min_component_size` | `int` | `64` |
| `fill_holes` | `bool` | `True` |
| `smooth_iterations` | `int` | `1` |
| `keep_largest_component` | `bool` | `False` |

#### [validate_spacing_zyx](../../src/robustness.py#L17)

`validate_spacing_zyx(spacing_zyx: tuple[float, float, float], *, min_spacing_mm: float=0.05, max_spacing_mm: float=10.0) → list[str]`

Static calls (including nested helper bodies): `zip`, `np.isfinite`, `ValueError`, `messages.append`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [_connected_components](../../src/robustness.py#L44)

`_connected_components(mask: np.ndarray) → tuple[np.ndarray, int]`

Static calls (including nested helper bodies): `ndimage.generate_binary_structure`, `ndimage.label`, `mask.astype`.

#### [_remove_small_components](../../src/robustness.py#L49)

`_remove_small_components(mask: np.ndarray, min_component_size: int) → np.ndarray`

Static calls (including nested helper bodies): `_connected_components`, `np.arange`, `ndimage.sum`, `np.isin`, `mask.astype`, `np.zeros_like`, `np.asarray`, `int`.

#### [_largest_component](../../src/robustness.py#L65)

`_largest_component(mask: np.ndarray) → np.ndarray`

Static calls (including nested helper bodies): `_connected_components`, `np.arange`, `ndimage.sum`, `int`, `np.zeros_like`, `np.argmax`.

#### [postprocess_binary_mask](../../src/robustness.py#L76)

`postprocess_binary_mask(mask: np.ndarray, *, min_component_size: int=64, fill_holes: bool=True, smooth_iterations: int=1, keep_largest_component: bool=False) → np.ndarray`

Static calls (including nested helper bodies): `ndimage.generate_binary_structure`, `mask.astype`, `_remove_small_components`, `cleaned.astype`, `_largest_component`, `ndimage.binary_fill_holes`, `ndimage.binary_opening`, `ndimage.binary_closing`, `int`.

#### [postprocess_multiclass_prediction](../../src/robustness.py#L102)

`postprocess_multiclass_prediction(probabilities: np.ndarray, predicted_labels: np.ndarray, *, class_configs: dict[int, LabelPostprocessConfig] \| None=None) → np.ndarray`

Static calls (including nested helper bodies): `int`, `np.zeros_like`, `range`, `probabilities.copy`, `masked_scores.argmax(axis=0).astype`, `ValueError`, `class_configs.get`, `postprocess_binary_mask`, `LabelPostprocessConfig`, `masked_scores.argmax`, `candidate_masks[1:].any`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [compute_entropy_uncertainty](../../src/robustness.py#L141)

`compute_entropy_uncertainty(probabilities: np.ndarray, *, epsilon: float=1e-08) → np.ndarray`

Static calls (including nested helper bodies): `np.clip`, `float`, `(entropy / max_entropy).astype`, `ValueError`, `probabilities.astype`, `np.sum`, `np.log`, `max`, `int`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [summarize_uncertainty](../../src/robustness.py#L154)

`summarize_uncertainty(uncertainty_map: np.ndarray, *, foreground_mask: np.ndarray \| None=None) → dict[str, object]`

Static calls (including nested helper bodies): `uncertainty_map.astype`, `values.mean`, `ValueError`, `np.any`, `values.reshape`, `foreground_mask.astype`, `float`, `selected.mean`, `selected.max`, `np.percentile`, `per_slice_mean.tolist`.

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

## [src/visualization.py](../../src/visualization.py)

Implementation module; see the linked source and module guide.

#### [apply_window](../../src/visualization.py#L15)

`apply_window(slice_hu: np.ndarray, center: float, width: float) → np.ndarray`

Static calls (including nested helper bodies): `np.clip`, `((clipped - lower) / (upper - lower)).astype`.

#### [save_hu_histogram](../../src/visualization.py#L22)

`save_hu_histogram(volume_hu: np.ndarray, output_path: str \| Path) → None`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `volume_hu.astype(np.float32).ravel`, `plt.subplots`, `axis.hist`, `axis.set_title`, `axis.set_xlabel`, `axis.set_ylabel`, `axis.axvline`, `axis.legend`, `fig.tight_layout`, `fig.savefig`, `plt.close`, `Path(output_path).expanduser` (additional calls in source).

#### [save_montage](../../src/visualization.py#L47)

`save_montage(volume_hu: np.ndarray, output_path: str \| Path, slices_per_row: int=8) → None`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `np.linspace`, `plt.subplots`, `enumerate`, `axes[0, 0].set_ylabel`, `axes[1, 0].set_ylabel`, `fig.suptitle`, `fig.tight_layout`, `fig.savefig`, `plt.close`, `len`, `np.asarray`, `apply_window` (additional calls in source).

### [AxialScrollViewer](../../src/visualization.py#L82)

Class contract is defined by the fields and methods below.

#### [AxialScrollViewer.__init__](../../src/visualization.py#L83)

`__init__(self, volume_hu: np.ndarray) → None`

Static calls (including nested helper bodies): `int`, `plt.subplots`, `self.ax_brain.imshow`, `self.ax_bone.imshow`, `self.ax_brain.set_title`, `self.ax_bone.set_title`, `self.ax_brain.axis`, `self.ax_bone.axis`, `self.fig.canvas.mpl_connect`, `self._draw`, `apply_window`.

#### [AxialScrollViewer._step](../../src/visualization.py#L110)

`_step(self, delta: int) → None`

Static calls (including nested helper bodies): `max`, `self._draw`, `min`.

#### [AxialScrollViewer._on_scroll](../../src/visualization.py#L114)

`_on_scroll(self, event: object) → None`

Static calls (including nested helper bodies): `getattr`, `self._step`.

#### [AxialScrollViewer._on_key_press](../../src/visualization.py#L121)

`_on_key_press(self, event: object) → None`

Static calls (including nested helper bodies): `getattr`, `self._step`.

#### [AxialScrollViewer._draw](../../src/visualization.py#L128)

`_draw(self) → None`

Static calls (including nested helper bodies): `self.im_brain.set_data`, `self.im_bone.set_data`, `self.fig.suptitle`, `self.fig.canvas.draw_idle`, `apply_window`.

#### [show_axial_scroll](../../src/visualization.py#L139)

`show_axial_scroll(volume_hu: np.ndarray) → AxialScrollViewer`

Static calls (including nested helper bodies): `AxialScrollViewer`, `plt.show`.

#### [save_day2_before_after](../../src/visualization.py#L145)

`save_day2_before_after(resampled_volume_hu: np.ndarray, cropped_volume_hu: np.ndarray, processed_volume: np.ndarray, crop_bbox_zyx: BoundingBox3D, output_path: str \| Path) → None`

Save visual QA image for Day 2 preprocessing.

The figure shows:
- pre-crop brain/bone windows on one slice,
- crop box overlay to verify anatomy preservation,
- post-crop + normalized result for comparison.

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `max`, `int`, `apply_window`, `plt.subplots`, `axes[0].imshow`, `axes[0].set_title`, `axes[0].axis`, `axes[1].imshow`, `axes[1].set_title`, `Rectangle`, `axes[1].add_patch`, `axes[1].axis` (additional calls in source).

#### [save_day3_slice_overlays](../../src/visualization.py#L213)

`save_day3_slice_overlays(volume_hu: np.ndarray, brain_mask_3d: np.ndarray, bone_mask_3d: np.ndarray, output_dir: str \| Path, max_slices: int \| None=None, min_representative_slices: int=10) → list[Path]`

Save per-slice overlay PNGs for qualitative review.

Parameters to tune:
- `max_slices`: optional cap on number of slices exported for very large studies.
- `min_representative_slices`: ensures enough coverage when a cap is active.

Static calls (including nested helper bodies): `Path(output_dir).expanduser().resolve`, `output_path.mkdir`, `int`, `np.arange`, `max`, `min`, `np.linspace`, `apply_window`, `brain_mask_3d[z_idx].astype`, `bone_mask_3d[z_idx].astype`, `plt.subplots`, `axis.imshow`, `np.any`, `axis.set_title` (additional calls in source).

#### [_to_numpy](../../src/visualization.py#L266)

`_to_numpy(array_like: object) → np.ndarray`

Static calls (including nested helper bodies): `hasattr`, `np.asarray`, `array_like.detach().cpu().numpy`, `array_like.detach().cpu`, `array_like.detach`.

#### [save_day4_batch_viz](../../src/visualization.py#L272)

`save_day4_batch_viz(batch: dict[str, object], output_path: str \| Path, title: str='Day 4 2.5D Batch Sanity Check', max_items: int=4) → None`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `_to_numpy(batch['image']).astype`, `_to_numpy(batch['mask']).astype`, `list`, `min`, `plt.subplots`, `range`, `fig.suptitle`, `fig.tight_layout`, `fig.savefig`, `plt.close`, `_to_numpy(batch['slice_index']).tolist`, `ValueError` (additional calls in source).

Explicit raised conditions: `ValueError`. See source for triggers; called validators may raise additional exceptions.

#### [save_day5_curves](../../src/visualization.py#L326)

`save_day5_curves(history: dict[str, list[float] \| list[int]], output_path: str \| Path) → None`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `np.asarray`, `plt.subplots`, `axes[0].plot`, `axes[0].set_title`, `axes[0].set_xlabel`, `axes[0].set_ylabel`, `axes[0].grid`, `axes[0].legend`, `axes[1].plot`, `axes[1].set_title`, `axes[1].set_xlabel`, `axes[1].set_ylabel` (additional calls in source).

#### [save_day5_prediction_overlays](../../src/visualization.py#L370)

`save_day5_prediction_overlays(center_slices: np.ndarray, predicted_labels: np.ndarray, reference_labels: np.ndarray, output_dir: str \| Path, slice_indices: list[int] \| None=None) → list[Path]`

Static calls (including nested helper bodies): `Path(output_dir).expanduser().resolve`, `output_path.mkdir`, `enumerate`, `list`, `np.clip`, `plt.subplots`, `axes[0].imshow`, `axes[0].set_title`, `axes[0].axis`, `axes[1].imshow`, `axes[1].set_title`, `axes[1].axis`, `axes[2].imshow`, `np.any` (additional calls in source).

#### [save_day7_prediction_overlays](../../src/visualization.py#L421)

`save_day7_prediction_overlays(center_slices: np.ndarray, predicted_labels: np.ndarray, output_dir: str \| Path, uncertainty: np.ndarray \| None=None) → list[Path]`

Static calls (including nested helper bodies): `Path(output_dir).expanduser().resolve`, `output_path.mkdir`, `range`, `int`, `np.clip`, `plt.subplots`, `np.atleast_1d`, `axes[0].imshow`, `axes[0].set_title`, `axes[0].axis`, `axes[1].imshow`, `axes[1].set_title`, `axes[1].axis`, `fig.tight_layout` (additional calls in source).

#### [save_report_slice_montage](../../src/visualization.py#L463)

`save_report_slice_montage(center_slices: np.ndarray, predicted_labels: np.ndarray, reference_labels: np.ndarray, uncertainty: np.ndarray \| None, slice_indices: list[int], output_path: str \| Path, *, title: str='Evaluation Montage') → Path`

Static calls (including nested helper bodies): `Path(output_path).expanduser().resolve`, `output_file.parent.mkdir`, `max`, `plt.subplots`, `enumerate`, `fig.suptitle`, `fig.tight_layout`, `fig.savefig`, `plt.close`, `len`, `np.asarray`, `np.clip`, `axes[row_index, 0].imshow`, `axes[row_index, 0].set_title` (additional calls in source).
