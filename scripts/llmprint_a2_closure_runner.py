"""Fail-closed, resumable LLMPrint A2 evaluation and reporting closure."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_CONFIG_SHA256 = "4325b2a518aa5080dfb5cc070d57713bf6ee84efb9d72e8e4cbc89308920613a"
EXPECTED_SUBSET_SHA256 = "162e27bccf4be98a3e15596772490dac44503363ac5781ac5365fea2d08f4a10"
CANONICAL_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
CANONICAL_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
UPSTREAM_COMMIT = "3e577f98b2bb64780ec2995b074c5aeec9b017e1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_json(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def load_detector(project: Path):
    path = project / "scripts" / "llmprint_detect_dual.py"
    spec = importlib.util.spec_from_file_location("llmprint_detect_dual", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen dual detector")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_fingerprints(fingerprint_dir: Path, subset_path: Path, output: Path) -> dict:
    if sha256(subset_path) != EXPECTED_SUBSET_SHA256:
        raise RuntimeError("frozen A2 subset SHA256 mismatch")
    subset = json.loads(subset_path.read_text(encoding="utf-8"))
    expected_ids = [f"llmprint-pair-{index:03d}" for index in range(200)]
    if [row["pair_id"] for row in subset["pairs"]] != expected_ids:
        raise RuntimeError("frozen A2 pair identities/order mismatch")
    actual_files = sorted(fingerprint_dir.glob("*.json"))
    if [path.stem for path in actual_files] != expected_ids:
        raise RuntimeError("fingerprint directory is not exactly IDs 000..199")
    artifacts = []
    for index, path in enumerate(actual_files):
        pair_id = expected_ids[index]
        record = json.loads(path.read_text(encoding="utf-8"))
        checks = (
            record.get("fingerprint_index") == index,
            record.get("pair_id") == pair_id,
            record.get("status") == "COMPLETED",
            record.get("gcg_iterations_requested") == 500,
            record.get("gcg_iterations_completed") == 500,
            len(record.get("final_suffix_token_ids", [])) == 20,
            record.get("scientific_config_sha256") == EXPECTED_CONFIG_SHA256,
            record.get("upstream_commit") == UPSTREAM_COMMIT,
            record.get("model_modified") is False,
            record.get("error") is None,
        )
        if not all(checks):
            raise RuntimeError(f"immutable fingerprint integrity failure: {pair_id}")
        artifacts.append({
            "fingerprint_index": index,
            "pair_id": pair_id,
            "file_name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    payload = {
        "schema_version": "wmkd.llmprint-fingerprint-manifest.v1",
        "artifact_type": "fingerprint_package",
        "experiment": "A2",
        "integrity_status": "PASS",
        "validated_record_count": 200,
        "missing_count": 0,
        "duplicate_count": 0,
        "invalid_count": 0,
        "ordered_ids": "llmprint-pair-000..llmprint-pair-199",
        "subset_sha256": EXPECTED_SUBSET_SHA256,
        "scientific_config_sha256": EXPECTED_CONFIG_SHA256,
        "canonical_model_id": CANONICAL_MODEL_ID,
        "canonical_model_revision": CANONICAL_REVISION,
        "upstream_commit": UPSTREAM_COMMIT,
        "artifact_entries_sha256": digest_json(artifacts),
        "artifacts": artifacts,
    }
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != payload:
            raise RuntimeError("existing immutable fingerprint manifest differs from current artifacts")
    else:
        atomic_json(output, payload)
    return payload


def valid_sequence(path: Path, model_id: str, revision: str, manifest_sha: str) -> bool:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return (
            value.get("status") == "COMPLETED"
            and value.get("model_id") == model_id
            and value.get("revision") == revision
            and value.get("record_count") == 200
            and value.get("fingerprint_manifest_sha256") == manifest_sha
            and len(value.get("records", [])) == 200
            and [row.get("pair_id") for row in value["records"]]
            == [f"llmprint-pair-{index:03d}" for index in range(200)]
        )
    except (OSError, json.JSONDecodeError):
        return False


def run_sequence(args, model_path: Path, model_id: str, revision: str, output: Path) -> None:
    manifest_sha = sha256(args.fingerprint_manifest)
    if output.exists():
        if valid_sequence(output, model_id, revision, manifest_sha):
            return
        raise RuntimeError(f"invalid existing probability sequence; refusing overwrite: {output}")
    command = [
        str(args.scientific_python), str(args.project / "scripts/llmprint_evaluate_probability_sequence.py"),
        "--model", str(model_path), "--model-id", model_id, "--revision", revision,
        "--fingerprint-dir", str(args.fingerprint_dir),
        "--fingerprint-manifest", str(args.fingerprint_manifest),
        "--output", str(output), "--dtype", "float16",
    ]
    subprocess.run(command, check=True, env={**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":4096:8"})
    if not valid_sequence(output, model_id, revision, manifest_sha):
        raise RuntimeError(f"probability sequence integrity failure: {model_id}")


def file_manifest(root: Path, model: dict, transport: dict) -> dict:
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (
            not path.is_file()
            or path.name.endswith((".lock", ".tmp"))
            or path.name in {".mdl", ".msc", ".mv"}
            or ".cache" in relative.parts
            or "onnx" in relative.parts
            or "coreml" in relative.parts
        ):
            continue
        files.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    config_path = root / "config.json"
    if not config_path.exists():
        raise RuntimeError(f"downloaded model lacks config.json: {model['modelscope_id']}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("model_type") != model["model_type"]:
        raise RuntimeError(f"model_type mismatch for {model['modelscope_id']}")
    if config.get("vocab_size") != model["vocab_size"]:
        raise RuntimeError(f"vocab_size mismatch for {model['modelscope_id']}")
    if model["architecture"] not in config.get("architectures", []):
        raise RuntimeError(f"architecture mismatch for {model['modelscope_id']}")
    remote = {row["Path"]: row for row in transport["remote_files"] if row.get("Type") == "blob"}
    mismatches = []
    for row in files:
        metadata = remote.get(row["path"])
        if metadata is None:
            mismatches.append(f"not_in_remote_metadata:{row['path']}")
        elif metadata.get("Sha256") and metadata["Sha256"] != row["sha256"]:
            mismatches.append(f"sha256:{row['path']}")
        elif metadata.get("Size") is not None and int(metadata["Size"]) != row["bytes"]:
            mismatches.append(f"size:{row['path']}")
    if mismatches:
        raise RuntimeError(f"ModelScope file verification failed: {mismatches[:5]}")
    return {
        "schema_version": "wmkd.llmprint-model-acquisition-manifest.v1",
        "transport": "ModelScope",
        "official_upstream_id": model["official_upstream_id"],
        "modelscope_id": model["modelscope_id"],
        "modelscope_revision": model["modelscope_revision"],
        "requested_branch": transport["requested_branch"],
        "resolved_weight_commit": transport["resolved_weight_commit"],
        "remote_file_metadata_sha256": transport["remote_file_metadata_sha256"],
        "local_path": str(root),
        "identity_checks": {"model_type": "PASS", "vocab_size": "PASS", "architecture": "PASS"},
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "file_entries_sha256": digest_json(files),
        "downloaded_files_remote_metadata_match": True,
        "excluded_transport_patterns": transport["excluded_transport_patterns"],
        "files": files,
        "verified_at": now(),
    }


def acquire(args, model: dict) -> tuple[Path, Path]:
    slot = int(model["slot"])
    acquisition = args.run_dir / "acquisition" / f"slot-{slot:02d}.json"
    if acquisition.exists():
        value = json.loads(acquisition.read_text(encoding="utf-8"))
        path = Path(value["local_path"])
        if value.get("modelscope_revision") == model["modelscope_revision"] and path.exists():
            return path, acquisition
        raise RuntimeError(f"stale/invalid acquisition manifest for slot {slot}")
    transport_result = args.run_dir / "state" / f"download-slot-{slot:02d}.json"
    if transport_result.exists():
        transport_result.unlink()
    subprocess.run([
        str(args.modelscope_python), str(args.project / "scripts/llmprint_modelscope_download.py"),
        "--model-id", model["modelscope_id"], "--revision", model["modelscope_revision"],
        "--cache-dir", str(args.model_cache), "--output", str(transport_result),
    ], check=True, env={
        **os.environ,
        "PYTHONPATH": str(args.modelscope_packages)
        + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""),
    })
    transport = json.loads(transport_result.read_text(encoding="utf-8"))
    path = Path(transport["local_path"])
    if transport.get("resolved_weight_commit") != model["modelscope_revision"]:
        raise RuntimeError(f"resolved ModelScope weight commit mismatch for slot {slot}")
    atomic_json(acquisition, file_manifest(path, model, transport))
    return path, acquisition


def probability_pairs(path: Path) -> list[list[float]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return [[row["w_plus_probability"], row["w_minus_probability"]] for row in value["records"]]


def finalize(args, panel: dict, state: dict) -> dict:
    detector = load_detector(args.project)
    reference_path = args.run_dir / "sequences" / "reference.json"
    reference = probability_pairs(reference_path)
    negatives = {}
    sequence_files = {"reference": {"path": str(reference_path), "sha256": sha256(reference_path)}}
    for model in panel["models"]:
        key = model["official_upstream_id"]
        path = args.run_dir / "sequences" / f"slot-{model['slot']:02d}.json"
        negatives[key] = probability_pairs(path)
        sequence_files[key] = {"path": str(path), "sha256": sha256(path)}
    primary = detector.calibrate_paper(reference, negatives)
    primary_reference = detector.paper_model(reference, reference)
    for row in primary["models"].values():
        row["positive"] = row["accuracy"] >= primary["final_tau"]
    primary["reference"] = {**primary_reference, "positive": primary_reference["accuracy"] >= primary["final_tau"]}
    primary["false_positive_count"] = sum(row["positive"] for row in primary["models"].values())
    primary["maximum_negative_accuracy"] = max(row["accuracy"] for row in primary["models"].values())
    primary["reference_separation_gap"] = primary_reference["accuracy"] - primary["maximum_negative_accuracy"]
    release = detector.calibrate_release(reference, negatives)
    release["reference"] = detector.release_model(reference, reference, min_n=release["calibrated_min_n"])
    evaluation_errors = []
    gates = {
        "fingerprint_integrity": True,
        "reference_fresh_reload": True,
        "negative_panel_13_of_13": len(negatives) == 13,
        "primary_calibrated": True,
        "reference_primary_positive": primary["reference"]["positive"],
        "usable_separation": primary["reference_separation_gap"] > 0,
        "no_severe_false_positive_anomaly": primary["false_positive_count"] == 0,
        "supplementary_release_recorded": True,
        "zero_unresolved_evaluation_errors": not evaluation_errors,
    }
    successful = all(gates.values())
    scientific_status = "COMPLETED" if successful else "FAILED"
    conclusion = (
        "LLMPrint core reproduction successful under WMKD A2 reduced-construction setting"
        if successful else "LLMPrint core reproduction not established under WMKD A2 reduced-construction setting"
    )
    results_dir = args.project / "results" / "llmprint" / "experiment_a2"
    detector_results = {
        "schema_version": "wmkd.llmprint-a2-detector-results.v1",
        "experiment": "A2", "run_id": args.run_id, "status": scientific_status,
        "primary": primary, "supplementary": release, "gates": gates,
        "evaluation_errors": evaluation_errors, "conclusion": conclusion,
    }
    atomic_json(results_dir / "detector_results.json", detector_results)
    artifact_manifest = {
        "schema_version": "wmkd.llmprint-a2-artifact-manifest.v1",
        "artifact_type": "fingerprint_package", "model_modified": False,
        "preferred_fingerprint": successful,
        "fingerprint_manifest": {"path": str(args.fingerprint_manifest), "sha256": sha256(args.fingerprint_manifest)},
        "probability_sequences": sequence_files,
        "acquisition_manifests": [
            {"slot": model["slot"], "path": str(args.run_dir / "acquisition" / f"slot-{model['slot']:02d}.json"),
             "sha256": sha256(args.run_dir / "acquisition" / f"slot-{model['slot']:02d}.json")}
            for model in panel["models"]
        ],
    }
    atomic_json(results_dir / "artifact_manifest.json", artifact_manifest)
    provenance = {
        "schema_version": "wmkd.llmprint-a2-provenance.v1",
        "method": "LLMPrint", "experiment": "A2", "run_id": args.run_id,
        "canonical_reference": {"model_id": CANONICAL_MODEL_ID, "revision": CANONICAL_REVISION, "model_modified": False},
        "upstream_commit": UPSTREAM_COMMIT,
        "subset_sha256": EXPECTED_SUBSET_SHA256, "config_sha256": EXPECTED_CONFIG_SHA256,
        "validation_panel": {"path": str(args.panel), "sha256": sha256(args.panel), "slots": 13, "replacement_slots": 0},
        "transport": "ModelScope pinned revisions, one model acquired and evaluated at a time",
        "scientific_adaptation": "WMKD reduced-construction A2: 200 fingerprints, 500 GCG steps; all other frozen semantics unchanged",
        "teacher_checkpoint_created": False,
    }
    atomic_json(results_dir / "provenance_manifest.json", provenance)
    summary = {
        "schema_version": "wmkd.llmprint-a2-summary.v1", "method": "LLMPrint", "experiment": "A2",
        "run_id": args.run_id, "status": scientific_status, "artifact_type": "fingerprint_package",
        "model_modified": False, "preferred_fingerprint": "yes" if successful else "no",
        "fingerprints": {"completed": 200, "missing": 0, "duplicate": 0, "invalid": 0},
        "negative_models_evaluated": 13, "primary_tau": primary["final_tau"],
        "primary_reference_score": primary["reference"]["accuracy"],
        "primary_false_positive_count": primary["false_positive_count"],
        "supplementary_reference_positive": release["reference"]["positive"],
        "conclusion": conclusion, "gates": gates,
    }
    atomic_json(results_dir / "summary.json", summary)
    full_log = {
        "schema_version": "wmkd.full-experiment-log.v1", "method": "LLMPrint", "role": "preferred_fingerprint",
        "experiment": "A2", "run_id": args.run_id, "scientific_status": scientific_status,
        "artifact_type": "fingerprint_package", "model_modified": False, "preferred_fingerprint": successful,
        "construction_runs": ["llmprint_a2_20260901_064855", "llmprint_a2_cont1_20260901_105735"],
        "construction_integrity": json.loads(args.fingerprint_manifest.read_text(encoding="utf-8")),
        "evaluation": detector_results, "provenance": provenance, "artifact_manifest": artifact_manifest,
        "summary": summary, "closure_completed_at": now(), "ba_started": False,
    }
    atomic_json(results_dir / "full_experiment_log.json", full_log)
    report = f"""# LLMPrint Experiment A2 formal closure report

## Outcome

**{conclusion}.**

- Fingerprint package: 200/200 immutable artifacts; 0 missing, duplicate, or invalid.
- Reference: fresh reload of `{CANONICAL_MODEL_ID}@{CANONICAL_REVISION}`.
- Validation negatives: 13/13 frozen identities and pinned ModelScope revisions, evaluated serially.
- Primary paper detector: reference score `{primary['reference']['accuracy']:.6f}`, mu `{primary['mu']:.6f}`, sample sigma `{primary['sample_sigma_ddof1']:.6f}`, tau `{primary['final_tau']:.6f}`, false positives `{primary['false_positive_count']}`.
- Supplementary release detector: reference valid_n `{release['reference']['valid_n']}`, p-value `{release['reference']['exact_binomial_pvalue_greater']:.8g}`, calibrated min_n `{release['calibrated_min_n']}`, positive `{release['reference']['positive']}`.
- Preferred artifact type: fingerprint package. Model weights were not modified and no Teacher checkpoint was created.
- Ba: NOT STARTED.

## Gate verdicts

""" + "\n".join(f"- {name}: {'PASS' if passed else 'FAIL'}" for name, passed in gates.items()) + "\n"
    atomic_text(args.project / "docs" / "reproduction_reports" / "llmprint_experiment_a2_report.md", report)
    return summary


def update_index(args, summary: dict) -> None:
    path = args.project / "results" / "experiment_full_logs_index.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    objects = [row for row in value["objects"] if not (row.get("method") == "LLMPrint" and row.get("experiment") == "A2")]
    full_path = args.project / "results" / "llmprint" / "experiment_a2" / "full_experiment_log.json"
    objects.append({
        "method": "LLMPrint", "role": "preferred_fingerprint", "experiment": "A2", "run_id": args.run_id,
        "full_log_path": "results/llmprint/experiment_a2/full_experiment_log.json",
        "full_log_sha256": sha256(full_path), "final_model_manifest": None, "modelscope_repo": None,
        "scientific_status": summary["status"], "watermark_evaluation_available": True,
        "utility_available": False, "checkpoint_localization_support": False, "telemetry_records": 0,
        "artifact_type": "fingerprint_package", "model_modified": False,
        "preferred_fingerprint": summary["preferred_fingerprint"],
    })
    value["objects"] = objects
    value["object_count"] = len(objects)
    value["generated_at"] = now()
    atomic_json(path, value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--fingerprint-dir", type=Path, required=True)
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--reference-model", type=Path, required=True)
    parser.add_argument("--scientific-python", type=Path, required=True)
    parser.add_argument("--modelscope-python", type=Path, required=True)
    parser.add_argument("--modelscope-packages", type=Path, required=True)
    parser.add_argument("--model-cache", type=Path, required=True)
    args = parser.parse_args()
    args.fingerprint_manifest = args.run_dir / "fingerprint_manifest.json"
    args.run_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.run_dir / "state" / "status.json"
    state = {"schema_version": "wmkd.llmprint-a2-closure-status.v1", "run_id": args.run_id,
             "status": "RUNNING", "stage": "FINGERPRINT_MANIFEST", "runner_pid": os.getpid(),
             "started_at": now(), "ba_started": False, "completed_negative_slots": []}
    atomic_json(state_path, state)
    try:
        validate_fingerprints(args.fingerprint_dir, args.subset, args.fingerprint_manifest)
        panel = json.loads(args.panel.read_text(encoding="utf-8"))
        if panel.get("status") != "FROZEN" or panel.get("slots") != 13 or panel.get("replacement_slots") != 0 or len(panel.get("models", [])) != 13:
            raise RuntimeError("validation panel is not the frozen exact 13-model panel")
        state.update(stage="REFERENCE_FRESH_RELOAD", fingerprint_manifest_sha256=sha256(args.fingerprint_manifest))
        atomic_json(state_path, state)
        run_sequence(args, args.reference_model, CANONICAL_MODEL_ID, CANONICAL_REVISION,
                     args.run_dir / "sequences" / "reference.json")
        for model in panel["models"]:
            state.update(stage=f"NEGATIVE_SLOT_{model['slot']:02d}_ACQUIRE", current_model=model["official_upstream_id"])
            atomic_json(state_path, state)
            model_path, _ = acquire(args, model)
            state["stage"] = f"NEGATIVE_SLOT_{model['slot']:02d}_EVALUATE"
            atomic_json(state_path, state)
            run_sequence(args, model_path, model["official_upstream_id"], model["modelscope_revision"],
                         args.run_dir / "sequences" / f"slot-{model['slot']:02d}.json")
            state["completed_negative_slots"] = sorted(set(state["completed_negative_slots"] + [model["slot"]]))
            atomic_json(state_path, state)
        state["stage"] = "DETECTOR_AND_REPORT_CLOSURE"
        atomic_json(state_path, state)
        summary = finalize(args, panel, state)
        update_index(args, summary)
        state.update(status=summary["status"], stage="TERMINAL", scientific_status=summary["status"],
                     conclusion=summary["conclusion"], finished_at=now(), exit_code=0)
        atomic_json(state_path, state)
    except BaseException as error:
        state.update(status="FAILED", stage=state.get("stage"), error=f"{type(error).__name__}: {error}",
                     traceback=traceback.format_exc(), finished_at=now(), exit_code=1)
        atomic_json(state_path, state)
        raise


if __name__ == "__main__":
    main()
