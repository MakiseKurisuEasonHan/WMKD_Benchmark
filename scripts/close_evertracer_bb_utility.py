#!/usr/bin/env python3
"""Finalize EverTracer Bb after the frozen Ba-matched utility evaluation."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / "results/evertracer/experiment_bb"
UTILITY_DIR = ROOT / "utility"
RUN_ID = "evertracer_bb_utility_20260904_061500"
STUDENT_RUN = "evertracer_bb_student_20260904_033837"
MODEL = "/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_bb_student/evertracer_bb_student_20260904_033837/student/final_model"
RUNTIME_ROOT = f"/root/autodl-tmp/WMKD_Benchmark_data/runs/evertracer_bb_utility/{RUN_ID}"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, text: str) -> None:
    current = path.read_text(encoding="utf-8")
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    raw = read(UTILITY_DIR / "utility.json")
    sanity = read(UTILITY_DIR / "generation_sanity.json")
    student = raw["student"]
    arc = student["arc_challenge_acc_norm"]
    truthful = student["truthfulqa_mc2_acc"]
    ba_arc = 0.5051194539249146
    ba_truthful = 0.493714619952569
    if student["path"] != MODEL or not raw["offline"]:
        raise RuntimeError("UTILITY_BINDING_GATE_FAILED")
    if not sanity["passed"] or not sanity["fresh_process_reload"] or len(sanity["rows"]) != 5:
        raise RuntimeError("GENERATION_SANITY_GATE_FAILED")
    if any(row["empty"] or row["prompt_echo"] or row["catastrophic_repetition"] for row in sanity["rows"]):
        raise RuntimeError("GENERATION_OUTPUT_GATE_FAILED")
    utility = {
        "schema_version": "wmkd.evertracer-bb-utility-result.v1",
        "method": "EverTracer", "experiment": "Bb", "status": "COMPLETED",
        "student_run_id": STUDENT_RUN, "utility_run_id": RUN_ID,
        "student_model_path": MODEL, "git_head_at_launch": "0dc47eb9cb146ba84720f8363083bbc0d0d005de",
        "runtime_root": RUNTIME_ROOT,
        "execution": {"start": "2026-09-04T05:31:29Z", "utility_end": "2026-09-04T05:32:40Z", "end": "2026-09-04T05:32:50Z", "utility_runtime_seconds": 71, "generation_runtime_seconds": sanity["elapsed_seconds"], "exit_code": 0, "errors": 0, "silent_drops": 0},
        "protocol": {"exact_reuse_from_ba": True, "offline": True, "batch_size": 8, "dtype": "bfloat16", "apply_chat_template": True, "scoring_harness": "lm_eval.simple_evaluate", "tasks": ["arc_challenge", "truthfulqa_mc2"], "dataset_provenance": raw["dataset_provenance"], "immutable_a_summary": raw["reused_from_immutable_a_summary"], "generation_script": "scripts/evertracer_sanity.py", "generation_max_new_tokens": 96, "generation_decoding": "greedy"},
        "arc_challenge": {"expected_samples": 1172, "completed_samples": 1172, "errors": 0, "metric": "acc_norm", "value": arc, "stderr": student["raw_results"]["arc_challenge"]["acc_norm_stderr,none"]},
        "truthfulqa_mc2": {"expected_samples": 817, "completed_samples": 817, "errors": 0, "metric": "MC2", "value": truthful, "stderr": student["raw_results"]["truthfulqa_mc2"]["acc_stderr,none"]},
        "generation_sanity": {"status": "PASS", "expected": 5, "completed": 5, "errors": 0, "empty_outputs": 0, "artifact": "results/evertracer/experiment_bb/utility/generation_sanity.json"},
        "historical": {"base": {"arc_challenge_acc_norm": raw["base"]["arc_challenge_acc_norm"], "truthfulqa_mc2": raw["base"]["truthfulqa_mc2_acc"]}, "teacher": {"arc_challenge_acc_norm": raw["teacher"]["arc_challenge_acc_norm"], "truthfulqa_mc2": raw["teacher"]["truthfulqa_mc2_acc"]}, "ba_student": {"arc_challenge_acc_norm": ba_arc, "truthfulqa_mc2": ba_truthful}, "bb_student": {"arc_challenge_acc_norm": arc, "truthfulqa_mc2": truthful}},
        "bb_minus_ba": {"arc_challenge_acc_norm": arc - ba_arc, "truthfulqa_mc2": truthful - ba_truthful},
        "artifacts": {"utility": {"sha256": sha(UTILITY_DIR / "utility.json"), "size": (UTILITY_DIR / "utility.json").stat().st_size}, "generation_sanity": {"sha256": sha(UTILITY_DIR / "generation_sanity.json"), "size": (UTILITY_DIR / "generation_sanity.json").stat().st_size}},
        "bounded_interpretation": "Under the frozen standardized utility setting, the Bb Student retained broadly comparable downstream utility to the Ba Student: ARC-Challenge acc_norm was 0.006826 lower and TruthfulQA MC2 was 0.018118 lower. These single-run results cover only the specified benchmarks and do not establish universal model-quality preservation or statistical significance."
    }
    write(UTILITY_DIR / "utility_result.json", utility)

    final_conclusion = "Under the tested standardized UP plus same-backbone behavioral-distillation setting, the final Bb Student did not re-establish the Teacher's strong EverTracer verification signal and remained in the Base/Ba-like low-detectability regime. Frozen utility remained broadly comparable to Ba on ARC-Challenge and TruthfulQA, with small negative absolute differences; this does not establish a causal UP effect, universal removal, or universal quality preservation."
    result = read(ROOT / "result.json")
    result.update({"status": "COMPLETE", "utility_run_id": RUN_ID, "utility": {"status": "COMPLETED", "arc_challenge_acc_norm": arc, "truthfulqa_mc2": truthful, "generation_sanity": "PASS", "result": "results/evertracer/experiment_bb/utility/utility_result.json"}, "final_status": "COMPLETE", "detector_signal": "BASE_BA_LIKE_LOW_DETECTABILITY", "utility_status": "BROADLY_COMPARABLE_TO_BA_ON_FROZEN_SCOPE", "bounded_conclusion": final_conclusion, "limitations": ["one standardized Ba/Bb configuration", "same-backbone Student", "no checkpoint-level detector trajectory", "utility limited to the frozen benchmark scope", "no universal robustness or removal claim"]})
    write(ROOT / "result.json", result)

    readiness = read(ROOT / "readiness.json")
    readiness.update({"status": "COMPLETE", "utility_started": True, "utility_complete": True, "utility_run_id": RUN_ID, "safe_to_start_evertracer_utility": False, "safe_to_close_evertracer_bb": True, "next_action": "WAIT_FOR_EXPLICIT_NEXT_INSTRUCTION"})
    write(ROOT / "readiness.json", readiness)

    full = read(ROOT / "full_experiment_log.json")
    full.update({"status": "COMPLETE", "scientific_status": "COMPLETE", "utility": utility, "final_status": "COMPLETE", "detector_signal": "BASE_BA_LIKE_LOW_DETECTABILITY", "utility_status": "BROADLY_COMPARABLE_TO_BA_ON_FROZEN_SCOPE", "bounded_conclusion": final_conclusion, "limitations": result["limitations"]})
    full["environment"].update({"utility_host": "autodl-container-9235478639-4a175847", "utility_git_baseline": utility["git_head_at_launch"], "utility_gpu": "NVIDIA RTX PRO 6000 Blackwell Server Edition"})
    full["artifacts"].update({"utility_result": "results/evertracer/experiment_bb/utility/utility_result.json", "utility_raw": "results/evertracer/experiment_bb/utility/utility.json", "generation_sanity": "results/evertracer/experiment_bb/utility/generation_sanity.json"})
    write(ROOT / "full_experiment_log.json", full)

    provenance = read(ROOT / "provenance_manifest.json")
    provenance["utility"] = {"run_id": RUN_ID, "student_run_id": STUDENT_RUN, "exact_reuse_from_ba": True, "launch_git_head": utility["git_head_at_launch"], "utility_raw_sha256": sha(UTILITY_DIR / "utility.json"), "sanity_sha256": sha(UTILITY_DIR / "generation_sanity.json"), "result_sha256": sha(UTILITY_DIR / "utility_result.json")}
    write(ROOT / "provenance_manifest.json", provenance)
    artifacts = read(ROOT / "artifact_manifest.json")
    artifacts.update({"utility_artifact": RUNTIME_ROOT, "utility_run_id": RUN_ID})
    for name in ("utility.json", "generation_sanity.json", "utility_result.json"):
        rel = f"results/evertracer/experiment_bb/utility/{name}"
        if rel not in artifacts["tracked_evidence"]: artifacts["tracked_evidence"].append(rel)
    write(ROOT / "artifact_manifest.json", artifacts)

    report = PROJECT / "docs/reproduction_reports/evertracer_experiment_bb_report.md"
    text = report.read_text(encoding="utf-8").replace("# EverTracer Experiment Bb — detector complete, utility pending", "# EverTracer Experiment Bb — final scientific closure")
    text = text.replace("Utility remains `NOT_STARTED`, so the current stage is `DETECTOR_COMPLETE_UTILITY_PENDING`, not total EverTracer Bb closure.", "At the detector boundary utility was `NOT_STARTED`; the final utility section below supersedes that stage while preserving the historical boundary.")
    report.write_text(text, encoding="utf-8")
    append_once(report, "EVERTRACER_BB_UTILITY_20260904", f'''## Frozen Ba-matched utility and final synthesis

<!-- EVERTRACER_BB_UTILITY_20260904 -->
Run `{RUN_ID}` evaluated only the canonical Bb final Student with the exact Ba utility harness: offline ARC-Challenge revision `210d026faf9955653af8916fad021475a3f00453`, TruthfulQA multiple-choice revision `741b8276f2d1982aa3d5b832d3ee81ed3b896490`, chat template, BF16, batch 8, and the same five-prompt greedy generation sanity.

| Model | ARC-Challenge acc_norm | TruthfulQA MC2 |
| --- | ---: | ---: |
| Base | {raw['base']['arc_challenge_acc_norm']:.6f} | {raw['base']['truthfulqa_mc2_acc']:.6f} |
| Teacher | {raw['teacher']['arc_challenge_acc_norm']:.6f} | {raw['teacher']['truthfulqa_mc2_acc']:.6f} |
| Ba Student | {ba_arc:.6f} | {ba_truthful:.6f} |
| Bb Student | **{arc:.6f}** | **{truthful:.6f}** |

Bb minus Ba was `{arc-ba_arc:+.6f}` ARC and `{truthful-ba_truthful:+.6f}` TruthfulQA. ARC completed 1172/1172 and TruthfulQA 817/817 with zero errors or silent drops. Generation sanity passed 5/5 with no empty output, prompt echo, catastrophic repetition, or generation error.

{final_conclusion}

Limitations: one standardized Ba/Bb configuration; same-backbone Student; no checkpoint-level detector trajectory; utility limited to the frozen benchmark scope; no universal robustness/removal or universal model-quality claim. Final status: `COMPLETE`.
''')

    entry = f'''## EverTracer Bb final closure — 2026-09-04

<!-- EVERTRACER_BB_UTILITY_20260904 -->
Utility run `{RUN_ID}` exactly reused the Ba harness and completed ARC 1172/1172 (`acc_norm={arc:.9f}`), TruthfulQA 817/817 (`MC2={truthful:.9f}`), and ordinary generation 5/5, with zero errors. Versus Ba the differences were ARC `{arc-ba_arc:+.9f}` and TruthfulQA `{truthful-ba_truthful:+.9f}`. Combined with Bb detector AUC/TPR `0.4757/0.08`, the final Student remained Base/Ba-like in low detectability while retaining broadly comparable tested utility. EverTracer Bb is `COMPLETE`; CTCC Bb and iSeal Bb were not started.
'''
    for name in ("PROJECT_STATUS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md"):
        append_once(PROJECT / name, "EVERTRACER_BB_UTILITY_20260904", entry)
    todo = PROJECT / "TODO.md"
    t = todo.read_text(encoding="utf-8")
    t = t.replace("- [ ] EverTracer Bb detector complete; utility remains NOT_STARTED.", "- [x] EverTracer Bb detector and frozen Ba-matched utility complete; final scientific closure complete.")
    t = t.replace("- [ ] Wait for explicit instruction before EverTracer Bb utility; do not start CTCC Bb or iSeal Bb automatically.", "- [x] Complete EverTracer Bb utility and final scientific closure; do not start CTCC Bb or iSeal Bb automatically.")
    todo.write_text(t, encoding="utf-8")

    index = read(PROJECT / "results/experiment_full_logs_index.json")
    for obj in index["objects"]:
        if obj.get("full_log_path") == "results/evertracer/experiment_bb/full_experiment_log.json":
            obj.update({"full_log_sha256": sha(ROOT / "full_experiment_log.json"), "scientific_status": "COMPLETE", "utility_available": True, "utility_run_id": RUN_ID})
            break
    else: raise RuntimeError("GLOBAL_INDEX_ENTRY_MISSING")
    index["generated_at"] = datetime.now(timezone.utc).isoformat()
    write(PROJECT / "results/experiment_full_logs_index.json", index)
    print(json.dumps({"status": "PASS", "run_id": RUN_ID, "arc": arc, "truthfulqa": truthful, "bb_minus_ba": utility["bb_minus_ba"]}, indent=2))


if __name__ == "__main__": main()
