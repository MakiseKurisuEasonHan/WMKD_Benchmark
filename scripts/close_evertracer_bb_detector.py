#!/usr/bin/env python3
"""Close the frozen EverTracer Bb detector stage without running utility."""
from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

PROJECT = Path("/root/autodl-tmp/WMKD_Benchmark")
DATA = Path("/root/autodl-tmp/WMKD_Benchmark_data")
RUN_ID = "evertracer_bb_detector_20260904_051046"
STUDENT_RUN = "evertracer_bb_student_20260904_033837"
RUN = DATA / "runs/evertracer_bb_detector" / RUN_ID
ROOT = PROJECT / "results/evertracer/experiment_bb"
OUT = ROOT / "detector"
STUDENT = DATA / "runs/evertracer_bb_student" / STUDENT_RUN / "student/final_model"
REFERENCE = DATA / "runs/evertracer/evertracer_a_20260828_223155/checkpoints/reference_merged"
NEIGHBORHOODS = DATA / "runs/evertracer/evertracer_a_20260828_223155_cont1/artifacts/frozen_neighborhoods.jsonl"
CONFIG = PROJECT / "configs/distillation/evertracer_ba_direct.yaml"
VERIFY = PROJECT / "scripts/evertracer_verify.py"
AGGREGATE = PROJECT / "scripts/evertracer_aggregate_verification.py"
START = "2026-09-04T05:12:40Z"
END = "2026-09-04T05:13:47Z"


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
    raw_path = RUN / "metrics/student_verification_raw.json"
    aggregate_path = RUN / "metrics/student_verification.json"
    ba_check_path = RUN / "metrics/ba_reaggregation_check.json"
    preflight_path = RUN / "config/frozen_detector_preflight.json"
    log_path = RUN / "logs/verification.log"
    raw, result, ba_check, preflight = map(read, (raw_path, aggregate_path, ba_check_path, preflight_path))
    scores = result.get("scores", [])
    if len(scores) != 200 or result.get("member_count") != 100 or result.get("nonmember_count") != 100:
        raise RuntimeError("SAMPLE_COMPLETION_GATE_FAILED")
    numeric = ("suspect_variation", "reference_variation", "calibrated_score")
    if not all(math.isfinite(float(row[key])) for row in scores for key in numeric):
        raise RuntimeError("NONFINITE_SCORE_GATE_FAILED")
    if result.get("suspect") != str(STUDENT) or result.get("reference") != str(REFERENCE):
        raise RuntimeError("MODEL_BINDING_GATE_FAILED")
    if preflight.get("status") != "READY" or preflight.get("neighborhoods_sha256") != "7834e3d77704951ea06501c2166e960fef2b147ced3d751a8e55f07ec7b3672b":
        raise RuntimeError("FROZEN_ASSET_GATE_FAILED")
    if ba_check.get("member_oriented_auc") != 0.4987 or ba_check.get("member_oriented_tpr_at_fpr_limit") != 0.06:
        raise RuntimeError("BA_REAGGREGATION_GATE_FAILED")

    auc = result["member_oriented_auc"]
    tpr = result["member_oriented_tpr_at_fpr_limit"]
    references = {
        "teacher": {"auc": 1.0, "tpr": 1.0},
        "base": {"auc": 0.4417, "tpr": 0.05},
        "ba_student": {"auc": 0.4987, "tpr": 0.06},
    }
    differences = {
        "bb_minus_teacher_auc": auc - 1.0,
        "bb_minus_base_auc": auc - 0.4417,
        "bb_minus_ba_auc": auc - 0.4987,
        "bb_minus_teacher_tpr": tpr - 1.0,
        "bb_minus_base_tpr": tpr - 0.05,
        "bb_minus_ba_tpr": tpr - 0.06,
    }
    file_identity = {
        "raw": {"path": str(raw_path), "size": raw_path.stat().st_size, "sha256": sha(raw_path)},
        "aggregate": {"path": str(aggregate_path), "size": aggregate_path.stat().st_size, "sha256": sha(aggregate_path)},
        "ba_reaggregation": {"path": str(ba_check_path), "size": ba_check_path.stat().st_size, "sha256": sha(ba_check_path)},
        "preflight": {"path": str(preflight_path), "size": preflight_path.stat().st_size, "sha256": sha(preflight_path)},
        "verification_log": {"path": str(log_path), "size": log_path.stat().st_size, "sha256": sha(log_path)},
    }
    detector = {
        "schema_version": "wmkd.evertracer-bb-detector-result.v1",
        "method": "EverTracer", "experiment": "Bb", "status": "COMPLETED",
        "student_run_id": STUDENT_RUN, "detector_run_id": RUN_ID,
        "student_model_path": str(STUDENT),
        "student_archive": "MakiseKurisuEasonHan/Llama-3.2-WMKD-EverTracer-Bb-Student",
        "git_head_at_launch": "1625408a31de94059b3a7e2d214f4f9e1abd3616",
        "execution": {"start": START, "end": END, "wall_runtime_seconds": 67, "inference_runtime_seconds": raw["elapsed_seconds"], "expected_samples": 200, "completed_samples": 200, "errors": 0, "nonfinite_scores": 0, "silent_drops": 0, "exit_code": 0, "peak_vram_bytes": raw["peak_vram_bytes"]},
        "frozen_detector": {
            "exact_reuse_from_a_ba": True,
            "verification_set": {"source": "EdinburghNLP/xsum@7d4d486c2f8ef850b1a11aead99b894ff3dd7da9", "members": "Dtr", "nonmembers": "Dunseen", "member_count": 100, "nonmember_count": 100, "split_seed": 48},
            "neighborhoods": str(NEIGHBORHOODS), "neighborhoods_sha256": preflight["neighborhoods_sha256"],
            "k": 5, "symmetric_variants_per_original": 10, "perturbation_fraction": 0.30,
            "max_length": 128, "evaluation_seed": 42,
            "reference_model": str(REFERENCE), "reference_manifest_sha256": preflight["reference_provenance"]["manifest_sha256"],
            "config": str(CONFIG), "config_sha256": sha(CONFIG),
            "verification_code_sha256": sha(VERIFY), "aggregation_code_sha256": sha(AGGREGATE),
            "score": "C = suspect_variation - reference_variation; member_score = -C",
            "operating_rule": "maximum member TPR at empirical FPR <= 0.05",
        },
        "metrics": {"member_oriented_auc": auc, "member_oriented_tpr_at_fpr_limit": tpr, "member_oriented_fpr": result["member_oriented_fpr"], "member_oriented_threshold": result["member_oriented_threshold"], "official_auc_nonmember_positive": result["official_auc_nonmember_positive"]},
        "references": references, "differences": differences,
        "artifacts": file_identity,
        "integrity": {"correct_bb_student": "PASS", "frozen_detector_config": "PASS", "sample_completion": "PASS", "no_silent_drops": "PASS", "finite_scores": "PASS", "ba_reaggregation": "PASS"},
        "conclusion_scope": "Final-Student detector evidence only; no checkpoint trajectory, utility result, universal removal, or causal attribution.",
        "bounded_interpretation": "Under the tested standardized Bb attack, the final Student remained close to the canonical Base/Ba detector regime and far from the strongly fingerprinted Teacher. Relative to Ba, Bb had a 0.0230 lower AUC and a 0.02 higher TPR at the same FPR limit; these mixed small changes do not establish a material increase in EverTracer evidence or a causal effect of UP.",
        "utility_status": "NOT_STARTED",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for source, name in ((raw_path, "student_verification_raw.json"), (aggregate_path, "student_verification.json"), (ba_check_path, "ba_reaggregation_check.json"), (preflight_path, "frozen_detector_preflight.json")):
        shutil.copyfile(source, OUT / name)
    write(OUT / "detector_result.json", detector)
    write(OUT / "detector_run_manifest.json", {"schema_version": "wmkd.evertracer-bb-detector-run-manifest.v1", "run_id": RUN_ID, "canonical_student_run": STUDENT_RUN, "launch_git_head": detector["git_head_at_launch"], "frozen_config_identity": detector["frozen_detector"], "runtime_artifacts": file_identity, "tracked_artifacts": {p.name: {"size": p.stat().st_size, "sha256": sha(p)} for p in sorted(OUT.glob("*.json")) if p.name not in {"detector_run_manifest.json"}}, "utility_started": False})

    readiness = read(ROOT / "readiness.json")
    readiness.update({"detector_started": True, "detector_complete": True, "detector_run_id": RUN_ID, "detector_auc": auc, "detector_tpr": tpr, "status": "DETECTOR_COMPLETE_UTILITY_PENDING", "safe_to_start_evertracer_utility": True, "utility_started": False, "next_action": "WAIT_FOR_EXPLICIT_UTILITY_INSTRUCTION"})
    write(ROOT / "readiness.json", readiness)

    overall = read(ROOT / "result.json")
    overall["status"] = "DETECTOR_COMPLETE_UTILITY_PENDING"
    overall["detector"] = {"status": "COMPLETED", "run_id": RUN_ID, "auc": auc, "tpr": tpr, "fpr_limit": 0.05, "sample_count": 200, "errors": 0, "result": "results/evertracer/experiment_bb/detector/detector_result.json"}
    overall["utility"] = {"status": "NOT_STARTED", "result": None}
    overall["bounded_conclusion"] = detector["bounded_interpretation"]
    write(ROOT / "result.json", overall)

    full = read(ROOT / "full_experiment_log.json")
    full["scientific_status"] = "DETECTOR_COMPLETE_UTILITY_PENDING"
    full["detector"] = detector
    full["utility"] = {"status": "NOT_STARTED", "result": None}
    full["artifacts"].update({"detector_result": "results/evertracer/experiment_bb/detector/detector_result.json", "detector_raw": "results/evertracer/experiment_bb/detector/student_verification_raw.json", "detector_aggregate": "results/evertracer/experiment_bb/detector/student_verification.json", "detector_run_manifest": "results/evertracer/experiment_bb/detector/detector_run_manifest.json"})
    full["bounded_conclusion"] = detector["bounded_interpretation"] + " Utility remains NOT_STARTED."
    write(ROOT / "full_experiment_log.json", full)

    provenance = read(ROOT / "provenance_manifest.json")
    provenance["detector"] = {"run_id": RUN_ID, "student_run_id": STUDENT_RUN, "exact_reuse_from_a_ba": True, "neighborhoods_sha256": preflight["neighborhoods_sha256"], "config_sha256": sha(CONFIG), "verification_code_sha256": sha(VERIFY), "aggregation_code_sha256": sha(AGGREGATE), "result_sha256": sha(OUT / "detector_result.json")}
    write(ROOT / "provenance_manifest.json", provenance)

    artifacts = read(ROOT / "artifact_manifest.json")
    artifacts["detector_artifact"] = str(RUN)
    artifacts["detector_run_id"] = RUN_ID
    for name in ("detector_result.json", "detector_run_manifest.json", "student_verification_raw.json", "student_verification.json", "ba_reaggregation_check.json", "frozen_detector_preflight.json"):
        rel = f"results/evertracer/experiment_bb/detector/{name}"
        if rel not in artifacts["tracked_evidence"]:
            artifacts["tracked_evidence"].append(rel)
    write(ROOT / "artifact_manifest.json", artifacts)

    report = PROJECT / "docs/reproduction_reports/evertracer_experiment_bb_report.md"
    text = report.read_text(encoding="utf-8").replace("# EverTracer Experiment Bb — Student training and archive closure", "# EverTracer Experiment Bb — detector complete, utility pending")
    report.write_text(text, encoding="utf-8")
    section = f"""## Formal frozen-detector evaluation

<!-- EVERTRACER_BB_DETECTOR_20260904 -->
Detector run `{RUN_ID}` evaluated only the canonical final Bb Student. It exactly reused the A/Ba reference model, 200 frozen XSum neighborhoods (Dtr 100 members, Dunseen 100 nonmembers; split seed 48), K=5 symmetric perturbation pairs, 30% perturbation fraction, max length 128, calibrated probability-variation score, and maximum TPR at empirical FPR ≤5%. The neighborhoods SHA256 was `{preflight['neighborhoods_sha256']}`. Reaggregation of the preserved Ba raw scores reproduced AUC/TPR `0.4987/0.06` before Bb inference.

| Model | AUC | TPR @ FPR≤5% |
| --- | ---: | ---: |
| EverTracer Teacher | 1.0000 | 1.00 |
| Canonical Base | 0.4417 | 0.05 |
| EverTracer Ba Student | 0.4987 | 0.06 |
| EverTracer Bb Student | **{auc:.4f}** | **{tpr:.2f}** |

Bb minus Teacher/Base/Ba AUC differences are `{differences['bb_minus_teacher_auc']:.4f}`, `{differences['bb_minus_base_auc']:+.4f}`, and `{differences['bb_minus_ba_auc']:+.4f}`. Corresponding TPR differences are `{differences['bb_minus_teacher_tpr']:.2f}`, `{differences['bb_minus_base_tpr']:+.2f}`, and `{differences['bb_minus_ba_tpr']:+.2f}`.

Under the tested standardized Bb attack, the final Student remained close to the canonical Base/Ba detector regime and far from the strongly fingerprinted Teacher. Relative to Ba, Bb had a 0.0230 lower AUC and a 0.02 higher TPR at the same FPR limit; these mixed small changes do not establish a material increase in EverTracer evidence or a causal effect of UP. AUC is not a watermark-retention percentage.

All 200 expected samples completed with zero errors, zero silent drops, and zero non-finite scores. Evidence is limited to the final Student; no checkpoint-level trajectory was measured. Utility remains `NOT_STARTED`, so the current stage is `DETECTOR_COMPLETE_UTILITY_PENDING`, not total EverTracer Bb closure.
"""
    append_once(report, "EVERTRACER_BB_DETECTOR_20260904", section)

    global_entry = f"""## EverTracer Bb detector complete — 2026-09-04

<!-- EVERTRACER_BB_DETECTOR_20260904 -->
Formal frozen-detector run `{RUN_ID}` evaluated the canonical Bb Student with exact A/Ba reference, neighborhoods, score, and FPR≤5% operating semantics. All 200/200 samples completed with zero errors/non-finite scores. Member-oriented AUC/TPR were `{auc:.4f}/{tpr:.2f}` versus Teacher `1.0000/1.00`, Base `0.4417/0.05`, and Ba `0.4987/0.06`. The Bb result remains close to Base/Ba and far from Teacher; no retention percentage, universal-removal claim, causal UP claim, or checkpoint disappearance claim is made. Stage: `DETECTOR_COMPLETE_UTILITY_PENDING`; utility, CTCC Bb, and iSeal Bb remain unstarted.
"""
    for name in ("PROJECT_STATUS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md"):
        append_once(PROJECT / name, "EVERTRACER_BB_DETECTOR_20260904", global_entry)

    todo = PROJECT / "TODO.md"
    todo_text = todo.read_text(encoding="utf-8")
    todo_text = todo_text.replace("- [ ] EverTracer Bb Student training/archive complete; detector and utility remain NOT_STARTED.", "- [ ] EverTracer Bb detector complete; utility remains NOT_STARTED.")
    todo_text = todo_text.replace("- [ ] Wait for explicit instruction before EverTracer Bb detector or utility; do not start CTCC Bb or iSeal Bb automatically.", "- [x] Complete EverTracer Bb frozen detector evaluation with 200/200 finite scores and canonical comparisons.\n- [ ] Wait for explicit instruction before EverTracer Bb utility; do not start CTCC Bb or iSeal Bb automatically.")
    todo.write_text(todo_text, encoding="utf-8")
    print(json.dumps({"status": "PASS", "run_id": RUN_ID, "auc": auc, "tpr": tpr, "stage": "DETECTOR_COMPLETE_UTILITY_PENDING"}, indent=2))


if __name__ == "__main__":
    main()
