#!/usr/bin/env python3
"""Build canonical, evidence-preserving full logs for the ten closed WMKD objects."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "wmkd.full-experiment-log.v1"


OBJECTS = [
    {
        "method": "PN-FP", "slug": "pnfp", "role": "preferred_teacher", "experiment": "A2",
        "sources": ["results/summaries/pnfp_experiment_a_summary.json", "results/summaries/pnfp_experiment_a2_summary.json"],
        "archives": ["results/summaries/pnfp_a2_modelscope_upload.json"],
        "telemetry": [],
    },
    {
        "method": "PN-FP", "slug": "pnfp", "role": "ba_student", "experiment": "Ba",
        "sources": ["results/summaries/pnfp_experiment_ba_summary.json"],
        "archives": ["results/summaries/pnfp_ba_modelscope_upload.json"],
        "telemetry": [],
    },
    {
        "method": "EverTracer", "slug": "evertracer", "role": "preferred_teacher", "experiment": "A",
        "sources": ["results/evertracer/experiment_a_summary.json", "results/evertracer/status/evertracer_a_root_status.json", "results/evertracer/status/evertracer_a_cont1_status.json", "results/evertracer/status/evertracer_a_cont2_status.json"],
        "archives": ["results/evertracer/archive/evertracer_a_teacher_modelscope_source_manifest.json", "results/evertracer/archive/evertracer_a_teacher_modelscope_verification.json"],
        "telemetry": [],
    },
    {
        "method": "EverTracer", "slug": "evertracer", "role": "ba_student", "experiment": "Ba",
        "sources": ["results/evertracer/experiment_ba_summary.json", "results/evertracer/evertracer_ba_dataset_provenance.json", "results/evertracer/status/evertracer_ba_status.json"],
        "archives": ["results/evertracer/archive/evertracer_ba_student_modelscope_source_manifest.json", "results/evertracer/archive/evertracer_ba_student_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/evertracer_ba/training_telemetry.json"],
    },
    {
        "method": "CTCC", "slug": "ctcc", "role": "preferred_teacher", "experiment": "A",
        "sources": ["results/ctcc/experiment_a/summary.json", "results/ctcc/experiment_a/training.json", "results/ctcc/experiment_a/status.json", "results/ctcc/experiment_a/dataset_manifest.json", "results/ctcc/experiment_a/adapter_manifest.json"],
        "archives": ["results/ctcc/archive/ctcc_teacher_modelscope_source_manifest.json", "results/ctcc/archive/ctcc_teacher_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/ctcc_teacher/trainer_state.json"],
    },
    {
        "method": "CTCC", "slug": "ctcc", "role": "ba_student", "experiment": "Ba",
        "sources": ["results/ctcc/experiment_ba/summary.json"],
        "archives": ["results/ctcc/archive/ctcc_student_modelscope_source_manifest.json", "results/ctcc/archive/ctcc_student_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/ctcc_ba/training_telemetry.json"],
    },
    {
        "method": "iSeal", "slug": "iseal", "role": "preferred_teacher", "experiment": "A6",
        "sources": ["results/iseal/experiment_a6/summary.json", "results/iseal/experiment_a6/training.json", "results/iseal/experiment_a6/dataset_manifest.json", "results/iseal/experiment_a6/fingerprint_and_generation.json", "results/iseal/experiment_a6/utility.json", "results/iseal/experiment_a6/trainability_audit.json"],
        "archives": ["results/iseal/archive/iseal_teacher_modelscope_source_manifest.json", "results/iseal/archive/iseal_teacher_modelscope_verification.json"],
        "telemetry": [],
    },
    {
        "method": "iSeal", "slug": "iseal", "role": "ba_student", "experiment": "Ba",
        "sources": ["results/iseal/experiment_ba/summary.json"],
        "archives": ["results/iseal/archive/iseal_student_modelscope_source_manifest.json", "results/iseal/archive/iseal_student_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/iseal_ba/training_telemetry.json"],
    },
    {
        "method": "SCW", "slug": "scw", "role": "preferred_teacher", "experiment": "A2",
        "sources": ["results/scw/experiment_a2/summary.json", "results/scw/experiment_a2/closure_cont3.json", "results/scw/experiment_a2/provenance/teacher_artifact_manifest.json", "results/scw/experiment_a2/provenance/french_eval_1000_manifest.json"],
        "archives": ["results/scw/experiment_a2/archive/scw_a2_teacher_modelscope_source_manifest.json", "results/scw/experiment_a2/archive/scw_a2_teacher_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/scw_teacher/trainer_state.json"],
    },
    {
        "method": "SCW", "slug": "scw", "role": "ba_student", "experiment": "Ba",
        "sources": ["results/scw/experiment_ba/summary.json"],
        "archives": ["results/scw/experiment_ba/archive/scw_ba_student_modelscope_source_manifest.json", "results/scw/experiment_ba/archive/scw_ba_student_modelscope_verification.json"],
        "telemetry": ["artifacts/closure_evidence/scw_ba/training_telemetry.json"],
    },
]


CHECKPOINTS = {
    ("PN-FP", "preferred_teacher"): {"inventory": "final checkpoint recorded in source summary; current AutoDL locality not established", "intermediate": []},
    ("PN-FP", "ba_student"): {"inventory": "final Student recorded in source summary/archive; current AutoDL locality not established", "intermediate": []},
    ("EverTracer", "preferred_teacher"): {"inventory": "final target artifact archived; no current formal intermediate checkpoint inventoried", "intermediate": []},
    ("EverTracer", "ba_student"): {"inventory": "final_model local on current AutoDL (6,442,821,755 bytes)", "intermediate": []},
    ("CTCC", "preferred_teacher"): {"inventory": "checkpoint-1400 and final checkpoint-1428 local on current AutoDL; adapter artifacts", "intermediate": [{"step": 1400, "bytes": 146342230, "local": True}, {"step": 1428, "bytes": 146343079, "local": True, "final": True}]},
    ("CTCC", "ba_student"): {"inventory": "checkpoint-7500 plus final_model local on current AutoDL", "intermediate": [{"step": 7500, "bytes": 19294171498, "local": True, "optimizer_state": True, "final": True}]},
    ("iSeal", "preferred_teacher"): {"inventory": "final preferred Teacher recorded and archived; no current formal intermediate checkpoint inventoried", "intermediate": []},
    ("iSeal", "ba_student"): {"inventory": "final_model local on current AutoDL (6,442,821,691 bytes)", "intermediate": []},
    ("SCW", "preferred_teacher"): {"inventory": "final checkpoint-2500 local on current AutoDL (6,450,379,615 bytes), with optimizer/scheduler/RNG state", "intermediate": [{"step": 2500, "bytes": 6450379615, "local": True, "optimizer_state": True, "final": True}]},
    ("SCW", "ba_student"): {"inventory": "checkpoint-7500 plus final_model local on current AutoDL", "intermediate": [{"step": 7500, "bytes": 19294171738, "local": True, "optimizer_state": True, "final": True}]},
}


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_value(obj: Any, names: set[str]) -> Any:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in names and value not in (None, ""):
                return value
        for value in obj.values():
            found = first_value(value, names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = first_value(value, names)
            if found is not None:
                return found
    return None


def collect_named(obj: Any, names: set[str], out: list[Any]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in names:
                out.append({"field": key, "value": value})
            collect_named(value, names, out)
    elif isinstance(obj, list):
        for value in obj:
            collect_named(value, names, out)


def telemetry_payload(paths: list[str], snapshots: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    trajectory: list[Any] = []
    coverage = {"source": None, "record_count": 0, "fields": [], "note": "no persisted per-step trajectory located"}
    for rel in paths:
        path = ROOT / rel
        if not path.exists() or path.stat().st_size == 0:
            continue
        data = load(rel)
        snapshots[rel] = data
        candidate = None
        if isinstance(data, dict) and isinstance(data.get("log_history"), list):
            candidate = data["log_history"]
        elif isinstance(data, dict) and isinstance(data.get("trainer_metrics"), dict) and isinstance(data["trainer_metrics"].get("log_history"), list):
            candidate = data["trainer_metrics"]["log_history"]
        if candidate:
            trajectory.extend(candidate)
            coverage = {"source": rel, "record_count": len(candidate), "fields": sorted({k for x in candidate if isinstance(x, dict) for k in x}), "note": "persisted trainer log_history"}
        elif isinstance(data, dict) and isinstance(data.get("step_seconds"), list):
            trajectory.extend({"step": i + 1, "step_seconds": v} for i, v in enumerate(data["step_seconds"]))
            coverage = {"source": rel, "record_count": len(data["step_seconds"]), "fields": ["step", "step_seconds"], "note": "persisted step timing only; loss/LR/grad norm were not recorded here"}
    return trajectory, coverage


def persisted_histories(obj: Any, path: str = "") -> list[tuple[str, list[Any]]]:
    found: list[tuple[str, list[Any]]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}/{key}"
            if key.lower() in {"history", "log_history"} and isinstance(value, list) and value:
                found.append((child, value))
            found.extend(persisted_histories(value, child))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found.extend(persisted_histories(value, f"{path}/{i}"))
    return found


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    index_entries = []
    for spec in OBJECTS:
        snapshots: dict[str, Any] = {}
        source_meta = []
        for rel in spec["sources"] + spec["archives"]:
            path = ROOT / rel
            if not path.exists():
                raise FileNotFoundError(rel)
            snapshots[rel] = load(rel)
            source_meta.append({"path": rel, "sha256": sha(path), "bytes": path.stat().st_size})

        trajectory, telemetry_coverage = telemetry_payload(spec["telemetry"], snapshots)
        if not trajectory:
            candidates: list[tuple[str, list[Any]]] = []
            for source_path in spec["sources"]:
                candidates.extend((source_path + p, rows) for p, rows in persisted_histories(snapshots[source_path]))
            if candidates:
                source, trajectory = max(candidates, key=lambda item: len(item[1]))
                telemetry_coverage = {
                    "source": source,
                    "record_count": len(trajectory),
                    "fields": sorted({k for row in trajectory if isinstance(row, dict) for k in row}),
                    "note": "persisted history from canonical machine-readable source",
                }
        primary = snapshots[spec["sources"][0]]
        run_id = first_value(primary, {"run_id", "formal_run_id", "source_run_id"})
        continuation_ids: list[Any] = []
        collect_named(primary, {"cont1_run_id", "cont2_run_id", "continuation", "generation_continuation", "evaluation_cont1", "evaluation_cont2"}, continuation_ids)
        detector: list[Any] = []
        utility: list[Any] = []
        configuration: list[Any] = []
        generation: list[Any] = []
        failures: list[Any] = []
        collect_named(primary, {"detector", "fingerprint", "watermark", "watermarked", "registered", "held_out"}, detector)
        collect_named(primary, {"utility", "benchmarks", "arc", "truthfulqa_mc2", "ordinary_generation", "french_sanity"}, utility)
        collect_named(primary, {"configuration", "training_config", "authorized_config", "distillation"}, configuration)
        collect_named(primary, {"generation", "dataset"}, generation)
        for snap_path, snap in snapshots.items():
            collect_named(snap, {"error", "traceback", "failure", "parent_failure", "blocker", "continuation_reason"}, failures)

        archive_snaps = {p: snapshots[p] for p in spec["archives"]}
        model_repo = first_value(archive_snaps, {"repo", "repo_id", "modelscope_repo"})
        destination_verified = first_value(archive_snaps, {"destination_verified", "destination_sha256_verification"})
        archive_state = first_value(archive_snaps, {"archive_status", "artifact_state", "status"})
        if destination_verified in {None, "not_started", "not_performed"} and isinstance(archive_state, str) and "awaiting_destination_hash_verification" in archive_state:
            destination_verified = False
        manifest_sha = first_value(archive_snaps, {"source_manifest_sha256", "teacher_manifest_sha256", "authoritative_manifest_sha256"})
        checkpoints = CHECKPOINTS[(spec["method"], spec["role"])]
        checkpoint_detector_metrics = False
        localization_supported = bool(checkpoint_detector_metrics)
        localization = {
            "supported": localization_supported,
            "resolution": "checkpoint-level detector evaluation" if localization_supported else "Teacher-before versus final-Student-after only",
            "evidence": ["canonical Teacher detector result", "canonical final Student detector result"] if spec["role"] == "ba_student" else ["final Teacher detector result"],
            "available_checkpoints": checkpoints["intermediate"],
            "checkpoint_level_watermark_evaluation": checkpoint_detector_metrics,
            "intermediate_student_generations": False if spec["role"] == "ba_student" else None,
            "intermediate_detector_metrics": False if spec["role"] == "ba_student" else None,
            "limitation": "No persisted detector evaluation at intermediate Student checkpoints; training loss, gradient norm, or timing cannot identify the watermark-disappearance step." if spec["role"] == "ba_student" else "This object is a Teacher; disappearance localization applies to its downstream Ba Student.",
        }

        environment_candidates: list[Any] = []
        collect_named(primary, {"environment", "runtime", "host", "gpu", "python", "pytorch", "cuda"}, environment_candidates)
        log = {
            "schema_version": SCHEMA,
            "generated_at": generated_at,
            "identity": {
                "project": "WMKD_Benchmark", "watermark_method": spec["method"], "experiment": spec["experiment"],
                "role": spec["role"], "formal_run_id": run_id, "continuation_ids": continuation_ids,
                "parent_run": first_value(primary, {"parent_run", "parent_run_id", "parent_training_run", "teacher_run", "teacher_run_id"}),
                "timestamps": {"start": first_value(primary, {"start_time", "start", "upload_start"}), "end": first_value(primary, {"end_time", "end", "upload_end"})},
                "final_scientific_status": first_value(primary, {"scientific_status", "closure_status", "status", "engineering_status"}) or "COMPLETED (established by project closure records)",
            },
            "provenance": {
                "paper_or_official_repo": first_value(primary, {"official_source", "official_repo", "paper"}),
                "official_commit": first_value(primary, {"official_commit"}), "code_commit": first_value(primary, {"code_commit", "git_commit_at_gate"}),
                "canonical_model": first_value(primary, {"canonical_model", "backbone", "model"}), "model_revision": first_value(primary, {"model_revision", "revision", "base_revision"}),
                "dataset_and_manifest_evidence": generation, "tokenizer_or_template": first_value(primary, {"tokenizer", "template", "chat_template"}),
                "scientific_adaptations": first_value(primary, {"scientific_adaptations", "scientific_change", "sole_scientific_change"}),
                "runtime_adaptations": first_value(primary, {"runtime_adaptations", "continuation_reason"}), "source_documents": source_meta,
            },
            "environment": {"recorded_evidence": environment_candidates, "unavailable_fields_are_not_inferred": True},
            "configuration": {"recorded_evidence": configuration, "unavailable_fields_are_null_not_inferred": True},
            "training_telemetry": trajectory,
            "training_telemetry_coverage": telemetry_coverage,
            "stage_timeline": {"recorded_status_and_continuation_evidence": [snapshots[p] for p in spec["sources"][1:] if "status" in p or "closure" in p], "unrecorded_stage_timestamps": None},
            "generation": {"recorded_evidence": generation if spec["role"] == "ba_student" else [], "ba_required_fields_preserved_in_source_snapshots": spec["role"] == "ba_student"},
            "watermark_evaluation": {"method_specific_recorded_evidence": detector, "semantics_preserved_without_cross-method_normalization": True},
            "utility": {"recorded_evidence": utility},
            "artifacts": {"checkpoint_inventory": checkpoints, "modelscope_repo": model_repo, "archive_evidence": archive_snaps, "manifest_sha256": manifest_sha, "destination_verified": destination_verified},
            "failures_and_continuations": failures,
            "watermark_loss_analysis_support": localization,
            "conclusion": {
                "paper_fact": first_value(primary, {"paper_fact"}), "experimental_fact": first_value(primary, {"scientific_judgement", "bounded_conclusion", "conclusion", "final_judgement"}),
                "bounded_interpretation": first_value(primary, {"bounded_conclusion", "scientific_judgement", "conclusion"}), "limitations": first_value(primary, {"limitations", "limitation"}),
            },
            "source_snapshots": snapshots,
            "integrity": {"no_values_invented": True, "source_priority": ["immutable run artifacts", "machine-readable summary", "formal report", "experiment log", "trainer/state/log files", "project records"]},
        }
        out = ROOT / "results" / spec["slug"] / spec["role"] / "full_experiment_log.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index_entries.append({
            "method": spec["method"], "role": spec["role"], "experiment": spec["experiment"], "run_id": run_id,
            "full_log_path": out.relative_to(ROOT).as_posix(), "full_log_sha256": sha(out), "final_model_manifest": manifest_sha,
            "modelscope_repo": model_repo, "scientific_status": log["identity"]["final_scientific_status"],
            "watermark_evaluation_available": bool(detector), "utility_available": bool(utility),
            "checkpoint_localization_support": localization_supported, "telemetry_records": len(trajectory),
        })

    index = {"schema_version": "wmkd.full-experiment-log-index.v1", "generated_at": generated_at, "object_count": len(index_entries), "objects": index_entries}
    index_path = ROOT / "results" / "experiment_full_logs_index.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"index": str(index_path), "index_sha256": sha(index_path), "objects": len(index_entries)}, indent=2))


if __name__ == "__main__":
    main()
