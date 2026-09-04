#!/usr/bin/env python3
"""Close EverTracer Bb Student training/archive without running evaluation."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

PROJECT = Path("/root/autodl-tmp/WMKD_Benchmark")
DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
RUN_ID = "evertracer_bb_student_20260904_033837"
RUN = DATA / "runs/evertracer_bb_student" / RUN_ID
ROOT = PROJECT / "results/evertracer/experiment_bb"
EVIDENCE = ROOT / "evidence"
ARCHIVE_SOURCE = DATA / "manifests/evertracer_bb_student_modelscope_archive.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def append_once(path: Path, marker: str, text: str) -> None:
    current = path.read_text(encoding="utf-8")
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    archive = read(ARCHIVE_SOURCE)
    student = read(RUN / "student_manifest.json")
    reload_info = read(RUN / "reload_validation.json")
    redownload_reload = read(RUN / "archive_redownload_reload.json")
    telemetry = read(RUN / "metrics/training_telemetry.json")
    exit_info = read(RUN / "training_exit.json")
    config = read(RUN / "config/frozen_config.json")
    if archive.get("EVERTRACER_BB_STUDENT_ARCHIVED") != "YES" or not archive.get("independent_redownload_verified"):
        raise RuntimeError("ARCHIVE_NOT_VERIFIED")
    if reload_info.get("status") != "PASS" or redownload_reload.get("status") != "PASS":
        raise RuntimeError("RELOAD_NOT_VERIFIED")
    if telemetry.get("steps") != 7500 or telemetry.get("trainer_metrics", {}).get("epoch") != 3.0 or not telemetry.get("finite_loss"):
        raise RuntimeError("TRAINING_TELEMETRY_GATE_FAILED")

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    copies = {
        "student_manifest.json": RUN / "student_manifest.json",
        "training_exit.json": RUN / "training_exit.json",
        "reload_validation.json": RUN / "reload_validation.json",
        "archive_redownload_reload.json": RUN / "archive_redownload_reload.json",
        "student_modelscope_archive.json": ARCHIVE_SOURCE,
    }
    for name, source in copies.items():
        shutil.copyfile(source, EVIDENCE / name)

    training_summary = {
        "schema_version": "wmkd.evertracer-bb-student-training-summary.v1",
        "status": "COMPLETED",
        "run_id": RUN_ID,
        "host": "autodl-container-9235478639-4a175847",
        "student_path": student["artifact"],
        "base_model": student["base_model"],
        "base_revision": student["base_revision"],
        "dataset_sha256": student["dataset_sha256"],
        "configuration": {
            "epochs": 3, "learning_rate": 1e-5, "precision": "bf16",
            "effective_batch_size": 8, "full_parameter": True, "lora": False,
            "seed": 42, "expected_steps": 7500, "resume": False,
        },
        "optimizer_steps": 7500,
        "train_loss": telemetry["trainer_metrics"]["train_loss"],
        "train_runtime_seconds": telemetry["trainer_metrics"]["train_runtime"],
        "finite_loss": telemetry["finite_loss"],
        "mean_step_seconds": telemetry["mean_step_seconds"],
        "peak_vram_bytes": telemetry["peak_vram_bytes"],
        "exit_code": exit_info["exit_code"],
        "source_config_sha256": sha(RUN / "config/frozen_config.json"),
        "student_manifest_sha256": sha(RUN / "student_manifest.json"),
    }
    write(ROOT / "training_summary.json", training_summary)

    result = {
        "schema_version": "wmkd.evertracer-bb-result.v1",
        "method": "EverTracer", "experiment": "Bb",
        "preprocessing_run_id": "evertracer_bb_20260903_130000",
        "student_run_id": RUN_ID,
        "status": "STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING",
        "training": {"status": "COMPLETED", "steps": 7500, "epochs": 3, "train_loss": telemetry["trainer_metrics"]["train_loss"], "finite_loss": True},
        "fresh_process_reload": {"status": "PASS", "nonfinite_count": 0, "parameter_count": reload_info["finite_weight_check"]["parameter_count"]},
        "student_archive": {"status": "COMPLETED", "EVERTRACER_BB_STUDENT_ARCHIVED": "YES", "repository": archive["repository"], "visibility": "PRIVATE", "independent_redownload_verified": True, "verification_directory": archive["verification_directory"], "redownload_reload": "PASS"},
        "detector": {"status": "NOT_STARTED", "result": None},
        "utility": {"status": "NOT_STARTED", "result": None},
        "bounded_conclusion": "Fresh canonical full-parameter Student training, integrity validation, private archive, independent redownload, and offline reload passed. Watermark retention and utility are not evaluated in this stage.",
    }
    write(ROOT / "result.json", result)

    readiness = read(ROOT / "readiness.json")
    readiness.update({
        "student_run_id": RUN_ID,
        "safe_to_start_evertracer_student_training": False,
        "student_training_started": True,
        "student_training_complete": True,
        "student_fresh_process_reload": "PASS",
        "student_archived": True,
        "student_archive_repository": archive["repository"],
        "student_archive_visibility": "PRIVATE",
        "student_archive_independent_redownload_verified": True,
        "detector_started": False, "utility_started": False,
        "status": "STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING",
        "next_action": "WAIT_FOR_EXPLICIT_DETECTOR_OR_UTILITY_INSTRUCTION",
    })
    write(ROOT / "readiness.json", readiness)

    artifacts = read(ROOT / "artifact_manifest.json")
    artifacts.update({
        "artifact_type": "student_training_and_archive_closure_package",
        "model_modified": True,
        "student_artifact": student["artifact"],
        "student_run_id": RUN_ID,
        "student_archive_repository": archive["repository"],
        "student_archive_verified": True,
    })
    for name in copies:
        rel = f"results/evertracer/experiment_bb/evidence/{name}"
        if rel not in artifacts["tracked_evidence"]:
            artifacts["tracked_evidence"].append(rel)
    artifacts["tracked_evidence"].extend(x for x in [
        "results/evertracer/experiment_bb/training_summary.json",
        "results/evertracer/experiment_bb/result.json",
    ] if x not in artifacts["tracked_evidence"])
    write(ROOT / "artifact_manifest.json", artifacts)

    provenance = read(ROOT / "provenance_manifest.json")
    provenance["student"] = {
        "run_id": RUN_ID, "base_model": student["base_model"], "base_revision": student["base_revision"],
        "sft_dataset_sha256": student["dataset_sha256"], "student_manifest_sha256": sha(RUN / "student_manifest.json"),
        "full_parameter": True, "resume": False, "fresh_process_reload": "PASS",
        "archive_repository": archive["repository"], "archive_visibility": "PRIVATE",
        "archive_manifest_sha256": archive["package_manifest_sha256"], "independent_redownload_verified": True,
    }
    write(ROOT / "provenance_manifest.json", provenance)

    full = read(ROOT / "full_experiment_log.json")
    full["status"] = "PARTIAL"
    full["scientific_status"] = "STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING"
    full["environment"]["student_training_host"] = "autodl-container-9235478639-4a175847"
    full["environment"]["student_training_git_baseline"] = "78617904d9d4029138cdb11cc0feb7526ffae897"
    full["environment"]["student_gpu"] = "NVIDIA RTX PRO 6000 Blackwell Server Edition"
    full["student_initialization"] = {"status": "PASS", "fresh_canonical": True, "resume": False, "artifact": student["artifact"], "base_revision": student["base_revision"]}
    full["training"] = training_summary
    full["reload_validation"] = reload_info
    full["student_archive"] = result["student_archive"] | {"package_manifest_sha256": archive["package_manifest_sha256"], "source_manifest_sha256": archive["source_manifest_sha256"]}
    full["detector"] = {"status": "NOT_STARTED", "result": None}
    full["utility"] = {"status": "NOT_STARTED", "result": None}
    full["artifacts"].update({"training_summary": "results/evertracer/experiment_bb/training_summary.json", "result": "results/evertracer/experiment_bb/result.json", "student_archive_evidence": "results/evertracer/experiment_bb/evidence/student_modelscope_archive.json"})
    full["bounded_conclusion"] = result["bounded_conclusion"]
    write(ROOT / "full_experiment_log.json", full)

    report = f"""# EverTracer Experiment Bb — Student training and archive closure

Preprocessing run `evertracer_bb_20260903_130000` remains the canonical processed20k source. It contains exactly 20,000 records; paired content/file/order SHA256 are `0f23881da975d7b8262599690c85cfb5d1a90b2c3c1976efcaa8f651aa064c55`, `41a44ffc153c5df78485037f154c4004f1b6f04b2451deac3c1c7ca9af6e6853`, and `49d42164d0aa254385d0d9b78596d7369a50ad6070d4e47e32b3f74c73a6be73`. SFT content/file SHA256 are `a4dd0c4dcd5141a62d380a6577083d48f80fb04c0e2a8b2b41f44dcb47bffff4` and `2fc1acd16f8e7239924948f48d420eca4b2ded50ae90aefec4f5fb0536a7f91f`; Ba/Bb parity passed 19/19 fields.

Student run `{RUN_ID}` started from fresh canonical `meta-llama/Llama-3.2-3B-Instruct@{student['base_revision']}` with no resume, adapter, Teacher weight, or prior Student initialization. Full-parameter BF16 SFT used three epochs, learning rate `1e-5`, effective batch size 8, and seed 42. Training completed 7,500/7,500 optimizer steps with exit code 0, finite loss throughout, final aggregate train loss `{telemetry['trainer_metrics']['train_loss']}`, and runtime `{telemetry['trainer_metrics']['train_runtime']}` seconds. The final trainer-state point recorded loss `0.6531`, gradient norm `10.875`, and learning rate `0`.

A separate fresh Python process loaded the final two-shard Student, scanned all `{reload_info['finite_weight_check']['parameter_count']:,}` parameters with zero non-finite values, found no adapter/LoRA files, and passed a neutral generation smoke (`The Moon`). Successful training and reload alone do not establish EverTracer watermark retention or utility.

After explicit authorization, the inference-ready Student was archived to PRIVATE ModelScope model repository `{archive['repository']}`. The package contains 18 allowed files: eight inference files, Llama license/NOTICE/model card, archive manifest/SHA256SUMS, and five non-secret provenance records. `training_args.bin`, checkpoints, optimizer/scheduler state, dataset/processed20k, cache, training log, secrets, credentials, and unrelated artifacts were excluded. A new independent directory `{archive['verification_directory']}` reproduced the complete canonical file set, every size, and every SHA256. Secret and large-file allowlist scans passed, and the redownloaded model independently loaded with all parameters finite and a passing neutral smoke.

`EVERTRACER_BB_PROCESSED20K_ARCHIVED = YES`.

`EVERTRACER_BB_STUDENT_ARCHIVED = YES`.

Current state is `STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING`. EverTracer detector and utility remain `NOT_STARTED`; CTCC Bb and iSeal Bb were not started. No watermark-retention or utility conclusion is claimed. Wait for the next explicit instruction.
"""
    (PROJECT / "docs/reproduction_reports/evertracer_experiment_bb_report.md").write_text(report, encoding="utf-8")

    project_marker = "EVERTRACER_BB_STUDENT_ARCHIVE_20260904"
    status_text = f"""## EverTracer Bb Student training/archive closure — 2026-09-04

<!-- {project_marker} -->
Fresh canonical full-parameter Student run `{RUN_ID}` completed 7,500/7,500 steps (3 epochs, BF16, LR 1e-5, effective batch 8, seed 42, no resume) with finite loss and fresh-process reload PASS. The inference-ready Student was uploaded only after PRIVATE confirmation to `{archive['repository']}`; a new independent download matched all 18 canonical filenames, sizes, and SHA256 values and passed offline reload. `EVERTRACER_BB_STUDENT_ARCHIVED = YES`. Status is `STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING`; detector, utility, CTCC Bb, and iSeal Bb remain NOT_STARTED, and no watermark or utility conclusion is claimed.
"""
    append_once(PROJECT / "PROJECT_STATUS.md", project_marker, status_text)
    append_once(PROJECT / "EXPERIMENT_LOG.md", project_marker, status_text)
    append_once(PROJECT / "CODEX_LOG.md", project_marker, status_text)

    todo = PROJECT / "TODO.md"
    todo_text = todo.read_text(encoding="utf-8")
    todo_text = todo_text.replace("- [ ] EverTracer Bb remains NOT RUN / deferred.", "- [ ] EverTracer Bb Student training/archive complete; detector and utility remain NOT_STARTED.")
    todo_text = todo_text.replace("- [ ] Wait for a separate explicit instruction before EverTracer Bb Student training; do not start detector, utility, CTCC Bb, or iSeal Bb automatically.", "- [x] Complete fresh EverTracer Bb Student training, fresh-process reload, PRIVATE Student archive, independent SHA verification, and offline redownload reload.\n- [ ] Wait for explicit instruction before EverTracer Bb detector or utility; do not start CTCC Bb or iSeal Bb automatically.")
    todo.write_text(todo_text, encoding="utf-8")

    print(json.dumps({"status": "PASS", "run_id": RUN_ID, "archive": archive["repository"], "files_written": 16}, indent=2))


if __name__ == "__main__":
    main()
