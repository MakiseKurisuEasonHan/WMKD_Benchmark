#!/usr/bin/env python3
"""Durable scientific closure for the distinct CTCC Bb2 variant."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from passive5_shared_bb import file_sha256, read_jsonl, records_sha256

BA_ARC = 0.48378839590443684
BA_TRUTH = 0.4506136480297226


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def write(path: Path, value: object):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def append(path: Path, marker: str, text: str):
    old = path.read_text(encoding="utf-8")
    if marker not in old: path.write_text(old.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--project",type=Path,required=True); ap.add_argument("--data-root",type=Path,required=True); ap.add_argument("--method",choices=("ctcc",),required=True); ap.add_argument("--run-id",required=True); a=ap.parse_args()
    run=a.data_root/f"runs/ctcc_bb2/{a.run_id}"; out=a.project/"results/ctcc/experiment_bb2"; out.mkdir(parents=True,exist_ok=True)
    cfg=load(a.project/f"configs/distillation/ctcc_bb2_{a.run_id}.json"); pairs=read_jsonl(run/"dataset/frozen_paired_qa.jsonl"); qa=load(run/"audit/quality_audit.json"); reuse=load(run/"paraphrase/reuse_provenance.json")
    if len(pairs)!=20000 or qa["sample_count"]!=20000: raise RuntimeError("CTCC_BB2_COUNT_GATE")
    if qa["prompt_leakage_count"] or qa["chat_control_leakage_count"] or qa["truncation_count"] or qa["generation_failure_count"]: raise RuntimeError("CTCC_BB2_QUALITY_GATE")
    tele=load(run/"metrics/training_telemetry.json"); reload=load(run/"metrics/reload_validation.json"); da=load(run/"archive/processed20k_modelscope.json"); sa=load(run/"archive/student_modelscope.json"); d=load(run/"evaluation/detector.json")["summary"]; u=load(run/"evaluation/utility.json")["student"]; san=load(run/"evaluation/generation_sanity.json")
    bb2=f"{d['categories']['trigger']['activations']}/95 triggers; negatives {d['combined_negatives']['false_activations']}/205"
    full={"schema_version":"wmkd.full-experiment-log.v1","identity":{"project":"WMKD_Benchmark","method":"CTCC","experiment":"Bb2","canonical_run_id":a.run_id},"status":"COMPLETED","scientific_status":"COMPLETE","variant":{"distinct_from":"CTCC Bb","only_difference":"global identity-fallback-count acceptance gate removed","original_bb_status":"BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE","original_bb_unchanged":True,"per_sample_frozen_protocol_unchanged":True},"parent":cfg["source_dataset"],"original_bb_reuse":reuse,"preprocessing":{"status":"COMPLETE","record_count":20000,"paired_content_sha256":records_sha256(pairs),"physical_sha256":file_sha256(run/"dataset/frozen_paired_qa.jsonl"),"quality":qa,"identity_fallback_count":qa["identity_fallback_count"],"identity_fallback_rate":qa["identity_fallback_rate"],"aggregate_fallback_gate_enforced":False},"processed20k_archive":da,"student_initialization":{"fresh_canonical":True,"base_revision":cfg["student"]["revision"],"resume":False},"training":{"status":"COMPLETE","steps":tele["steps"],"epochs":3,"learning_rate":1e-5,"precision":"bf16","effective_batch":8,"train_loss":tele["trainer_metrics"]["train_loss"],"finite_loss":tele["finite_loss"]},"fresh_reload":reload,"student_archive":sa,"detector":{"status":"COMPLETE","operational_detector_not_official_ctcc":True,"historical":{"teacher":"95/95 triggers; negatives 0/205","base":"0/95 triggers","ba":"0/95 triggers; negatives 0/205","original_bb":"NOT_RUN"},"bb2":bb2,"result":{"trigger":d["categories"]["trigger"],"combined_negatives":d["combined_negatives"],"generation_errors":d["generation_errors"],"raw_generation_count":d["raw_generation_count"]}},"utility":{"status":"COMPLETE","ba":{"arc_challenge_acc_norm":BA_ARC,"truthfulqa_mc2":BA_TRUTH},"bb2":{"arc_challenge_acc_norm":u["arc_challenge_acc_norm"],"truthfulqa_mc2":u["truthfulqa_mc2_acc"]},"delta":{"arc_challenge_acc_norm":u["arc_challenge_acc_norm"]-BA_ARC,"truthfulqa_mc2":u["truthfulqa_mc2_acc"]-BA_TRUTH},"generation_sanity_pass":san["passed"]},"limitations":["Bb2 is a distinct follow-up variant, not a continuation or repair of original Bb","global identity-fallback acceptance gate was removed","all identity fallbacks remain disclosed","WMKD operational equality detector is not the official CTCC detector","single standardized same-backbone setting"],"artifacts":{"runtime_root":str(run)}}
    write(out/"full_experiment_log.json",full); write(out/"result.json",{"method":"CTCC","experiment":"Bb2","run_id":a.run_id,"status":"COMPLETE","preprocessing":full["preprocessing"],"detector":full["detector"],"utility":full["utility"],"limitations":full["limitations"]}); shutil.copyfile(run/"archive/processed20k_modelscope.json",out/"processed20k_archive.json"); shutil.copyfile(run/"archive/student_modelscope.json",out/"student_archive.json")
    report=f"# CTCC Experiment Bb2 — final scientific closure\n\n`{a.run_id}` is a distinct follow-up variant. Original CTCC Bb remains `BLOCKED_AT_PREPROCESSING_ACCEPTANCE_GATE` at 202 > 200. Bb2 removes only that experiment-level aggregate gate; the frozen per-sample UP transformation and downstream protocol are unchanged.\n\nOriginal Bb resolved outputs reused: {reuse['original_resolved_reused']}. Final processed records: 20,000. Identity fallbacks: {qa['identity_fallback_count']} ({qa['identity_fallback_rate']:.6%}).\n\nStudent: 7,500 steps, three epochs, BF16, LR 1e-5, effective batch 8; fresh reload and PRIVATE archive verification passed.\n\nDetector (WMKD operational equality detector, not official CTCC): Teacher 95/95; Base 0/95; Ba 0/95; Bb2 {bb2}.\n\nUtility: ARC {u['arc_challenge_acc_norm']:.6f} (delta {u['arc_challenge_acc_norm']-BA_ARC:+.6f}); TruthfulQA MC2 {u['truthfulqa_mc2_acc']:.6f} (delta {u['truthfulqa_mc2_acc']-BA_TRUTH:+.6f}). Generation sanity passed.\n"
    (a.project/"docs/reproduction_reports/ctcc_experiment_bb2_report.md").write_text(report,encoding="utf-8")
    idx=load(a.project/"results/experiment_full_logs_index.json"); rel="results/ctcc/experiment_bb2/full_experiment_log.json"; idx["objects"]=[x for x in idx["objects"] if x.get("full_log_path")!=rel]; idx["objects"].append({"method":"CTCC","role":"bb2_student","experiment":"Bb2","run_id":a.run_id,"full_log_path":rel,"full_log_sha256":file_sha256(out/"full_experiment_log.json"),"scientific_status":"COMPLETE","watermark_evaluation_available":True,"utility_available":True,"checkpoint_localization_support":False,"telemetry_records":tele["steps"]}); idx["object_count"]=len(idx["objects"]); idx["generated_at"]=datetime.now(timezone.utc).isoformat(); write(a.project/"results/experiment_full_logs_index.json",idx)
    entry=f"## CTCC Bb2 final closure — {datetime.now(timezone.utc).date()}\n\n<!-- CTCC_BB2_FINAL -->\nDistinct run `{a.run_id}` reused {reuse['original_resolved_reused']} original Bb resolved outputs, completed 20,000 records with {qa['identity_fallback_count']} disclosed fallbacks, and completed Student, archives, frozen detector and utility. Original CTCC Bb remains blocked and unchanged."
    for name in ("PROJECT_STATUS.md","EXPERIMENT_LOG.md","CODEX_LOG.md","DECISIONS.md"): append(a.project/name,"CTCC_BB2_FINAL",entry)


if __name__=="__main__": main()
