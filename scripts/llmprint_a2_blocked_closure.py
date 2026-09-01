"""Finalize a fail-closed LLMPrint A2 closure when the frozen panel is unavailable."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--panel", type=Path, required=True)
    args = parser.parse_args()
    status_path = args.run_dir / "state" / "status.json"
    failed = json.loads(status_path.read_text(encoding="utf-8"))
    completed = failed.get("completed_negative_slots", [])
    if failed.get("status") != "FAILED" or completed != [1, 2, 3, 4, 5, 6]:
        raise RuntimeError("blocked closure requires preserved slot-7 failure after exact slots 1..6")
    fingerprint_manifest = args.run_dir / "fingerprint_manifest.json"
    manifest = json.loads(fingerprint_manifest.read_text(encoding="utf-8"))
    if manifest.get("integrity_status") != "PASS" or manifest.get("validated_record_count") != 200:
        raise RuntimeError("fingerprint integrity is not 200/200 PASS")
    reference = args.run_dir / "sequences" / "reference.json"
    if json.loads(reference.read_text(encoding="utf-8")).get("record_count") != 200:
        raise RuntimeError("Reference sequence is incomplete")
    sequences = {"reference": {"path": str(reference), "sha256": sha256(reference)}}
    for slot in completed:
        path = args.run_dir / "sequences" / f"slot-{slot:02d}.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("record_count") != 200:
            raise RuntimeError(f"slot {slot} sequence is incomplete")
        sequences[f"slot-{slot:02d}"] = {"path": str(path), "sha256": sha256(path)}
    blocker = {
        "type": "FROZEN_RESOURCE_PROVENANCE_BLOCKER",
        "stage": "NEGATIVE_SLOT_07_ACQUIRE",
        "model_id": "microsoft/phi-2",
        "frozen_modelscope_revision": "1650c3d781609187dc5133d1baf8fdf2921b874b",
        "evidence": "Frozen revision is absent from the ModelScope blob-revision set. The resolve/<hash> URL returns master content (same ETag), so treating it as pinned would be a silent revision change.",
        "policy": "No master fallback, replacement, panel change, or detector calibration from an incomplete panel.",
    }
    results = args.project / "results" / "llmprint" / "experiment_a2"
    detector = {
        "schema_version": "wmkd.llmprint-a2-detector-results.v1", "experiment": "A2",
        "run_id": args.run_id, "status": "BLOCKED", "primary": None, "supplementary": None,
        "negative_models_evaluated": 6, "negative_models_required": 13,
        "detector_status": "NOT_CALIBRATED_INCOMPLETE_FROZEN_PANEL", "blocker": blocker,
        "scientific_conclusion": "NOT_JUDGED",
    }
    atomic_json(results / "detector_results.json", detector)
    artifact = {
        "schema_version": "wmkd.llmprint-a2-artifact-manifest.v1", "artifact_type": "fingerprint_package",
        "model_modified": False, "preferred_fingerprint": False,
        "fingerprint_manifest": {"path": str(fingerprint_manifest), "sha256": sha256(fingerprint_manifest)},
        "probability_sequences": sequences, "immutable_completed_negative_slots": completed,
        "unresolved_negative_slots": list(range(7, 14)), "blocker": blocker,
    }
    atomic_json(results / "artifact_manifest.json", artifact)
    provenance = {
        "schema_version": "wmkd.llmprint-a2-provenance.v1", "method": "LLMPrint", "experiment": "A2",
        "run_id": args.run_id,
        "canonical_reference": {"model_id": "meta-llama/Llama-3.2-3B-Instruct", "revision": "0cb88a4f764b7a12671c53f0838cd831a0843b95", "model_modified": False},
        "upstream_commit": "3e577f98b2bb64780ec2995b074c5aeec9b017e1",
        "subset_sha256": manifest["subset_sha256"], "config_sha256": manifest["scientific_config_sha256"],
        "validation_panel": {"path": str(args.panel), "sha256": sha256(args.panel), "required_slots": 13,
                             "evaluated_slots": 6, "replacement_slots": 0},
        "teacher_checkpoint_created": False, "ba_started": False, "blocker": blocker,
    }
    atomic_json(results / "provenance_manifest.json", provenance)
    summary = {
        "schema_version": "wmkd.llmprint-a2-summary.v1", "method": "LLMPrint", "experiment": "A2",
        "run_id": args.run_id, "status": "BLOCKED", "terminal": True,
        "artifact_type": "fingerprint_package", "model_modified": False, "preferred_fingerprint": "no",
        "fingerprints": {"completed": 200, "missing": 0, "duplicate": 0, "invalid": 0},
        "reference_fresh_reload": "PASS", "negative_models_evaluated": 6,
        "negative_models_required": 13, "detector_status": detector["detector_status"],
        "scientific_conclusion": "NOT_JUDGED", "blocker": blocker,
    }
    atomic_json(results / "summary.json", summary)
    full = {
        "schema_version": "wmkd.full-experiment-log.v1", "method": "LLMPrint",
        "role": "preferred_fingerprint", "experiment": "A2", "run_id": args.run_id,
        "scientific_status": "BLOCKED", "terminal": True, "artifact_type": "fingerprint_package",
        "model_modified": False, "preferred_fingerprint": False,
        "construction_runs": ["llmprint_a2_20260901_064855", "llmprint_a2_cont1_20260901_105735"],
        "construction_integrity": manifest, "evaluation": detector, "provenance": provenance,
        "artifact_manifest": artifact, "summary": summary, "closure_completed_at": now(), "ba_started": False,
    }
    atomic_json(results / "full_experiment_log.json", full)
    report = f"""# LLMPrint Experiment A2 formal closure report

## Outcome

**Terminal status: BLOCKED. Scientific reproduction was not judged.**

- Immutable fingerprint package: 200/200 PASS; no regeneration or overwrite.
- Canonical Reference fresh reload: PASS.
- Frozen validation negatives evaluated: 6/13, each with an atomic 200-record sequence.
- Primary paper detector: not calibrated because the frozen panel is incomplete.
- Supplementary release detector: not calibrated because the frozen panel is incomplete.
- Preferred fingerprint: no scientific preference decision; no Teacher checkpoint exists.
- Ba: NOT STARTED.

## Blocker

Slot 7 requires `microsoft/phi-2@1650c3d781609187dc5133d1baf8fdf2921b874b`. That revision is absent from the ModelScope blob-revision set. A direct `resolve/<hash>` request silently returns current master content, demonstrated by the identical ETag. Using it would violate the frozen-panel rule. No replacement, master fallback, panel change, or tuning was performed.
"""
    atomic_text(args.project / "docs" / "reproduction_reports" / "llmprint_experiment_a2_report.md", report)
    index_path = args.project / "results" / "experiment_full_logs_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    objects = [row for row in index["objects"] if not (row.get("method") == "LLMPrint" and row.get("experiment") == "A2")]
    objects.append({"method": "LLMPrint", "role": "preferred_fingerprint", "experiment": "A2",
                    "run_id": args.run_id, "full_log_path": "results/llmprint/experiment_a2/full_experiment_log.json",
                    "full_log_sha256": sha256(results / "full_experiment_log.json"), "final_model_manifest": None,
                    "modelscope_repo": None, "scientific_status": "BLOCKED", "watermark_evaluation_available": False,
                    "utility_available": False, "checkpoint_localization_support": False, "telemetry_records": 0,
                    "artifact_type": "fingerprint_package", "model_modified": False, "preferred_fingerprint": "no"})
    index.update(generated_at=now(), object_count=len(objects), objects=objects)
    atomic_json(index_path, index)
    preserved = args.run_dir / "state" / "status_slot7_failed.json"
    if not preserved.exists():
        atomic_json(preserved, failed)
    failed.update(status="BLOCKED", terminal=True, stage="TERMINAL_BLOCKED", scientific_status="NOT_JUDGED",
                  detector_status=detector["detector_status"], blocker=blocker, finished_at=now(), exit_code=0)
    failed.pop("error", None); failed.pop("traceback", None)
    atomic_json(status_path, failed)


if __name__ == "__main__":
    main()
