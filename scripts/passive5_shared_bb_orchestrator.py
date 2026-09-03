#!/usr/bin/env python3
"""Fail-closed stage plan and collision checks for a future detached Shared Bb run."""
from __future__ import annotations
import argparse, json
from pathlib import Path
try:
    from scripts.passive5_shared_bb import UNRESOLVED_REVISIONS, load_config, validate_training_parity
except ModuleNotFoundError:
    from passive5_shared_bb import UNRESOLVED_REVISIONS, load_config, validate_training_parity

STAGES = ("preflight", "source-validation", "training-parity", "qwen-revision-validation", "paraphrase-pilot", "pilot-audit",
          "full-paraphrasing", "paraphrase-freeze", "quality-audit", "fresh-student-preflight",
          "student-adapter", "student-training", "fresh-reload", "llmprint", "reef", "huref", "awm", "zeroprint",
          "utility", "full-log", "report", "project-records", "git-closure")


def build_plan(project: Path, data_root: Path, run_id: str, config_path: Path, dry_run: bool) -> dict:
    config = load_config(config_path)
    ba = json.loads((project / "configs/distillation/passive5_shared_ba.json").read_text(encoding="utf-8"))
    parity = validate_training_parity(ba, config)
    run_root = data_root / "runs/passive5_shared_bb" / run_id
    if run_root.exists(): raise FileExistsError(f"RUN_COLLISION {run_root}")
    if not dry_run and config["paraphraser"]["revision"] in UNRESOLVED_REVISIONS:
        raise RuntimeError("FAIL_CLOSED_QWEN_REVISION_NOT_FROZEN")
    student = run_root / "student/final_model"; evaluation = run_root / "evaluation"
    commands = {
        "source-validation": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "validate-source", "--source", config["source_dataset"]["path"]],
        "training-parity": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "parity", "--ba-config", str(project/"configs/distillation/passive5_shared_ba.json")],
        "paraphrase-pilot": ["python", "scripts/passive5_shared_bb_paraphrase_runner.py", "--config", str(config_path), "--source", config["source_dataset"]["path"], "--journal", str(run_root/"pilot/attempts.jsonl"), "--backend", "qwen", "--limit", "200"],
        "pilot-audit": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "audit-journal", "--source", config["source_dataset"]["path"], "--journal", str(run_root/"pilot/attempts.jsonl"), "--output-dir", str(run_root/"pilot/audit")],
        "full-paraphrasing": ["python", "scripts/passive5_shared_bb_paraphrase_runner.py", "--config", str(config_path), "--source", config["source_dataset"]["path"], "--journal", str(run_root/"paraphrase/attempts.jsonl"), "--backend", "qwen"],
        "paraphrase-freeze": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "freeze", "--source", config["source_dataset"]["path"], "--journal", str(run_root/"paraphrase/attempts.jsonl"), "--output", str(run_root/"dataset/frozen_paired_qa.jsonl")],
        "quality-audit": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "quality-audit", "--pairs", str(run_root/"dataset/frozen_paired_qa.jsonl"), "--output-dir", str(run_root/"audit")],
        "student-adapter": ["python", "scripts/passive5_shared_bb.py", "--config", str(config_path), "adapt-student", "--pairs", str(run_root/"dataset/frozen_paired_qa.jsonl"), "--output", str(run_root/"dataset/student_qa.jsonl")],
        "student-training": ["python", "scripts/train_distillation_student.py", "--model-path", config["student"]["path"], "--dataset", str(run_root/"dataset/student_qa.jsonl"), "--output-dir", str(run_root/"student"), "--batch-size", "8", "--epochs", "3", "--learning-rate", "1e-5", "--seed", "42", "--max-length", "1024", "--telemetry", str(run_root/"metrics/training_telemetry.json")],
        "detectors": [["python", "scripts/passive5_ba_method_eval.py", "--project", str(project), "--student", str(student), "--output", str(evaluation), "--parent-run-id", run_id, "--run-id", run_id, "--method", method, "--experiment", "Bb"] for method in ("reef","huref","awm","zeroprint")],
        "llmprint": {"sequence_command": ["python", "scripts/llmprint_evaluate_probability_sequence.py", "--model", str(student), "--model-id", "WMKD/Passive5-Shared-Bb-Student", "--revision", config["student"]["revision"], "--fingerprint-dir", "/root/autodl-tmp/WMKD_Benchmark_data/runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1", "--fingerprint-manifest", "/root/autodl-tmp/WMKD_Benchmark_data/runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1/fingerprint_manifest.json", "--output", str(evaluation/"llmprint/student_probability_sequence.json"), "--dtype", "float16"], "comparison": "reuse frozen A2 reference bits and tau=0.7150049776126003; no recalibration", "recalibration": False},
        "utility": ["python", "scripts/scw_ba_utility.py", "--base", config["student"]["path"], "--teacher", config["student"]["path"], "--student", str(student), "--batch-size", "8", "--output", str(evaluation/"utility_results.json")]
    }
    return {"identity":"passive5_shared_bb", "run_id":run_id, "status":"DRY_RUN_ONLY" if dry_run else "READY_TO_LAUNCH",
            "gpu_run_started":False, "formal_bb_started":False, "stage_order":list(STAGES), "training_parity":parity,
            "fail_closed_on_stage_error":True, "single_large_gpu_stage":True, "commands":commands}


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("--project",type=Path,required=True);p.add_argument("--data-root",type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--config",type=Path,required=True);p.add_argument("--dry-run",action="store_true",required=True)
    p.add_argument("--output",type=Path);a=p.parse_args(); plan=build_plan(a.project,a.data_root,a.run_id,a.config,a.dry_run)
    text=json.dumps(plan,indent=2,ensure_ascii=False)+"\n"; print(text,end="")
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding="utf-8")

if __name__=="__main__":main()
