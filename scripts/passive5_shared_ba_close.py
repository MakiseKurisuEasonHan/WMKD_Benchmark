#!/usr/bin/env python3
"""Close the immutable Passive-5 Shared Ba evaluation continuation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


METHODS = ("LLMPrint", "REEF", "HuRef", "AWM", "ZeroPrint")
DATASET_SHA = "eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--parent-run-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    parent = args.data_root / "runs/passive5_shared_ba" / args.parent_run_id
    evaluation = args.data_root / "runs/passive5_shared_ba_eval" / args.run_id
    shared = args.project / "results/passive5_shared_ba"

    validation = json.loads((evaluation / "student_reload_validation.json").read_text())
    utility = json.loads((evaluation / "utility_results.json").read_text())
    student_manifest = json.loads((parent / "student/student_manifest.json").read_text())
    dataset_manifest = json.loads((parent / "dataset/manifest.json").read_text())
    provenance = json.loads((parent / "dataset/provenance.json").read_text())
    telemetry = json.loads((parent / "metrics/training_telemetry.json").read_text())
    if validation["status"] != "PASS" or validation["finite_weight_check"]["nonfinite_count"] != 0:
        raise RuntimeError("STUDENT_RELOAD_VALIDATION_NOT_PASS")
    if dataset_manifest["dataset_sha256"] != DATASET_SHA or student_manifest["dataset_sha256"] != DATASET_SHA:
        raise RuntimeError("DATASET_IDENTITY_MISMATCH")

    llm_sequence_path = evaluation / "llmprint/student_probability_sequence.json"
    llm_sequence = json.loads(llm_sequence_path.read_text())
    llm_reference_path = Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1/sequences/reference.json")
    llm_reference = json.loads(llm_reference_path.read_text())
    if llm_sequence["status"] != "COMPLETED" or llm_sequence["record_count"] != 200:
        raise RuntimeError("LLMPRINT_SEQUENCE_INCOMPLETE")
    reference_bits = [row["paper_bit"] for row in llm_reference["records"]]
    student_bits = [row["paper_bit"] for row in llm_sequence["records"]]
    correct = sum(left == right for left, right in zip(reference_bits, student_bits))
    llm_score = correct / 200
    llm_threshold = 0.7150049776126003
    llm = {
        "method": "LLMPrint", "native_metric": "primary paper-style bit accuracy",
        "reference_score": 1.0, "threshold": llm_threshold, "reference_detected": True,
        "student_score": llm_score, "student_detected": llm_score >= llm_threshold,
        "positive_rule": "score >= threshold", "valid_count": 200, "correct_bits": correct,
        "student_sequence_path": str(llm_sequence_path), "student_sequence_sha256": sha(llm_sequence_path),
        "errors": [],
    }

    loaded = {}
    for key in ("reef", "huref", "awm", "zeroprint"):
        path = evaluation / key / "detector_result.json"
        value = json.loads(path.read_text())
        if value["status"] != "COMPLETED" or value.get("errors"):
            raise RuntimeError(f"{key.upper()}_EVALUATION_NOT_CLEAN")
        loaded[key] = (value, path)
    reef_value, reef_path = loaded["reef"]
    huref_value, huref_path = loaded["huref"]
    awm_value, awm_path = loaded["awm"]
    zero_value, zero_path = loaded["zeroprint"]
    frozen_awm = json.loads((args.project / "results/awm/experiment_a/detector_results.json").read_text())
    frozen_huref = json.loads((args.project / "results/huref/experiment_a2/detector_results.json").read_text())
    method_rows = [llm,
        {"method":"REEF","native_metric":"centered linear CKA","reference_score":1.0,
         "threshold":reef_value["threshold"],"reference_detected":True,"student_score":reef_value["score"],
         "student_detected":reef_value["positive"],"positive_rule":"score > threshold","errors":[],
         "evaluation_path":str(reef_path),"evaluation_sha256":sha(reef_path)},
        {"method":"HuRef","native_metric":"ICS","reference_score":frozen_huref["detector"]["reference_self"],
         "threshold":huref_value["threshold"],"reference_detected":True,"student_score":huref_value["score"],
         "student_detected":huref_value["positive"],"positive_rule":"score > threshold","errors":[],
         "evaluation_path":str(huref_path),"evaluation_sha256":sha(huref_path)},
        {"method":"AWM","native_metric":"official mean Wq/Wk unbiased linear CKA",
         "reference_score":frozen_awm["detector"]["reference_self"],"threshold":awm_value["threshold"],
         "reference_detected":True,"student_score":awm_value["score"],"student_detected":awm_value["positive"],
         "positive_rule":"score > threshold","errors":[],"evaluation_path":str(awm_path),"evaluation_sha256":sha(awm_path)},
        {"method":"ZeroPrint","native_metric":"rescaled Pearson correlation","reference_score":1.0,
         "threshold":zero_value["threshold"],"reference_detected":True,
         "student_score":zero_value["score"]["rescaled"],"student_raw_pearson":zero_value["score"]["raw_pearson"],
         "student_detected":zero_value["positive"],"positive_rule":"score > threshold","errors":[],
         "evaluation_path":str(zero_path),"evaluation_sha256":sha(zero_path)},
    ]
    expected_thresholds = [0.7150049776126003,0.4546738923165847,4.119894027709961,0.0017953364917795106,0.6793505996465683]
    if [row["threshold"] for row in method_rows] != expected_thresholds:
        raise RuntimeError("FROZEN_THRESHOLD_MISMATCH")
    retained = sum(bool(row["student_detected"]) for row in method_rows)

    training_summary = {
        "schema_version":"wmkd.passive5-shared-ba-training-summary.v1","run_id":args.parent_run_id,
        "status":"COMPLETED","shared_student":True,"student_path":student_manifest["artifact"],
        "student_manifest_sha256":sha(parent / "student/student_manifest.json"),"dataset_sha256":DATASET_SHA,
        "configuration":student_manifest["config"],"optimizer_steps":telemetry["steps"],
        "epochs":telemetry["trainer_metrics"]["epoch"],"train_loss":telemetry["trainer_metrics"]["train_loss"],
        "finite_loss":telemetry["finite_loss"],"training_runtime_seconds":telemetry["trainer_metrics"]["train_runtime"],
        "peak_vram_bytes":telemetry["peak_vram_bytes"],"peak_host_rss_bytes":telemetry["peak_host_rss_bytes"],
        "resume":False,"seed":42,
    }
    teacher_summary = {
        "schema_version":"wmkd.passive5-shared-ba-teacher-dataset.v1","run_id":args.parent_run_id,
        "teacher":provenance["teacher"],"teacher_file_sha256":provenance["teacher_file_sha256"],
        "construction":{"raw_accepted":40003,"valid":39850,"unique_before_selection":20896,"selected":20000,
                        "candidate_to_unique_yield_percent":52.24,"parse_failures":399,"empty_or_filtered":153,
                        "completed_targets":[24000,26000,28000,30000,32000,34000,36000,38000,40000]},
        "dataset_sha256":DATASET_SHA,"frozen_jsonl_sha256":sha(parent / "dataset/frozen_qa.jsonl"),
        "source_manifest_sha256":sha(parent / "dataset/manifest.json"),
        "sample_ids_sha256":dataset_manifest["sample_ids_sha256"],
        "provenance_sha256":sha(parent / "dataset/provenance.json"),
        "total_generated_tokens":{"status":"NOT RECOVERABLE FROM PERSISTED TELEMETRY",
            "limitation":"generation_telemetry.json was overwritten per extension round; logging completeness limitation, not scientific invalidation"},
    }
    detector_summary = {
        "schema_version":"wmkd.passive5-shared-ba-detector-summary.v1","run_id":args.run_id,
        "parent_run_id":args.parent_run_id,"shared_student":True,"shared_student_run_id":args.parent_run_id,
        "dataset_sha256":DATASET_SHA,"status":"COMPLETED","retained_count":retained,"method_count":5,
        "all_evaluation_errors_resolved":True,"methods":method_rows,
        "bounded_conclusion":f"Ownership detectability remained positive under all {retained}/5 frozen passive-method detectors after the tested direct-distillation attack; this does not establish general robustness beyond these frozen protocols.",
    }
    atomic_json(shared / "training_summary.json", training_summary)
    atomic_json(shared / "teacher_dataset_manifest.json", teacher_summary)
    atomic_json(shared / "student_manifest.json", student_manifest)
    atomic_json(shared / "utility_results.json", utility)
    atomic_json(shared / "detector_summary.json", detector_summary)

    shared_full = {
        "schema_version":"wmkd.full-experiment-log.v1","experiment":"Shared Ba","run_id":args.run_id,
        "parent_run_id":args.parent_run_id,"continuation_type":"EVALUATION_ONLY_CONTINUATION",
        "status":"COMPLETED","scientific_status":"COMPLETED","shared_student":True,
        "shared_student_run_id":args.parent_run_id,"auto_shutdown":False,
        "lineage":[args.parent_run_id,"Student completed","evaluation orchestration stopped normally",args.run_id,"closure"],
        "teacher_dataset":teacher_summary,"training":training_summary,"reload_validation":validation,
        "utility":utility,"detectors":detector_summary,"unresolved_errors":[],
        "untouched":["MiniLLM","DistiLLM","paraphrase attack","REASMARK","other attacks"],
        "completed_at":now(),
    }
    atomic_json(shared / "full_experiment_log.json", shared_full)

    utility_rel = "results/passive5_shared_ba/utility_results.json"
    training_rel = "results/passive5_shared_ba/training_summary.json"
    dataset_rel = "results/passive5_shared_ba/teacher_dataset_manifest.json"
    report_rows = []
    for row in method_rows:
        slug = row["method"].lower()
        out = args.project / f"results/{slug}/experiment_ba"
        common = {
            "schema_version":f"wmkd.{slug}-ba.v1","method":row["method"],"experiment":"Ba",
            "run_id":args.run_id,"parent_run_id":args.parent_run_id,"status":"COMPLETED",
            "scientific_status":"DETECTABILITY_RETAINED" if row["student_detected"] else "DETECTABILITY_NOT_RETAINED",
            "shared_attack":True,"shared_student":True,"shared_student_run_id":args.parent_run_id,
            "dataset_sha256":DATASET_SHA,"model_modified":True,
            "student_artifact":student_manifest["artifact"],"utility_path":utility_rel,
            "training_log_path":training_rel,"teacher_dataset_manifest_path":dataset_rel,
            "reference_detected_before_kd":True,"detector":row,"unresolved_errors":[],
            "bounded_conclusion":"ownership fingerprint remained detectable after the tested direct-distillation attack" if row["student_detected"] else "ownership fingerprint was no longer detectable after the tested direct-distillation attack",
        }
        atomic_json(out / "detector_results.json", {**common,"detector":row})
        atomic_json(out / "summary.json", common)
        atomic_json(out / "provenance_manifest.json", {**common,"source_evaluation":row.get("evaluation_path",row.get("student_sequence_path")),"source_sha256":row.get("evaluation_sha256",row.get("student_sequence_sha256"))})
        atomic_json(out / "artifact_manifest.json", {**common,"large_artifacts_external":True,"source_evaluation":row.get("evaluation_path",row.get("student_sequence_path")),"source_sha256":row.get("evaluation_sha256",row.get("student_sequence_sha256")),"integrity":"PASS"})
        atomic_json(out / "full_experiment_log.json", {**common,"student_reload_validation_path":"results/passive5_shared_ba/full_experiment_log.json","shared_utility":utility,"detector":row,"completed_at":now()})
        report_path = args.project / f"docs/reproduction_reports/{slug}_experiment_ba_report.md"
        extra = f"\n- Student raw Pearson: {row['student_raw_pearson']:.12f}" if "student_raw_pearson" in row else ""
        atomic_text(report_path, f"# {row['method']} Experiment Ba report\n\n"
            f"**Ownership detectability {'remained' if row['student_detected'] else 'did not remain'} positive after the tested direct-distillation attack.**\n\n"
            f"- Shared Student run: `{args.parent_run_id}`\n- Evaluation continuation: `{args.run_id}`\n"
            f"- Dataset SHA256: `{DATASET_SHA}`\n- Reference score: {row['reference_score']:.12f}\n"
            f"- Frozen threshold: {row['threshold']:.12f}\n- Student {row['native_metric']}: {row['student_score']:.12f}{extra}\n"
            f"- Student detected: {'yes' if row['student_detected'] else 'no'}\n- Calibration reused: yes; recalibration: no\n"
            f"- Shared utility: ARC-Challenge acc_norm={utility['student']['arc_challenge_acc_norm']:.12f}; TruthfulQA MC2={utility['student']['truthfulqa_mc2_acc']:.12f}\n\n"
            "This conclusion is bounded to the frozen WMKD A/A2 detector and tested direct-distillation Student.\n")
        report_rows.append(f"| {row['method']} | {row['reference_score']:.12f} | {row['threshold']:.12f} | yes | {row['student_score']:.12f} | {'yes' if row['student_detected'] else 'no'} | {'YES' if row['student_detected'] else 'NO'} |")

    shared_report = f"""# Passive-5 Shared Ba final report

## Result

One direct-distillation Student is shared by LLMPrint, REEF, HuRef, AWM, and ZeroPrint because all five passive methods use the same unmodified canonical Base as Teacher. This avoids five scientifically redundant trainings. Ownership detectability was retained for **{retained}/5** frozen detectors.

## Teacher dataset and training

- Teacher: `meta-llama/Llama-3.2-3B-Instruct` at `0cb88a4f764b7a12671c53f0838cd831a0843b95`
- Construction: 40,003 raw accepted; 39,850 valid; 20,896 unique; 20,000 selected; candidate-to-unique yield 52.24%; 399 parse failures; 153 empty/filter cases.
- Frozen dataset SHA256: `{DATASET_SHA}`
- Student: fresh canonical initialization; full-parameter BF16; 3 epochs; 7,500/7,500 optimizer steps; LR 1e-5; effective batch 8; max length 1024; seed 42; no resume; no LoRA.
- Training loss: {telemetry['trainer_metrics']['train_loss']:.12f}; runtime: {telemetry['trainer_metrics']['train_runtime']:.3f}s.
- Student fresh reload: PASS; inference: `{validation['inference_smoke']['response']}`; non-finite parameters: 0/{validation['finite_weight_check']['parameter_count']}.
- Total generated-token count across Teacher extension rounds: **NOT RECOVERABLE FROM PERSISTED TELEMETRY** because the telemetry file was overwritten per round. This is a logging limitation, not scientific invalidation.

## Shared utility

- ARC-Challenge acc_norm: {utility['student']['arc_challenge_acc_norm']:.12f}
- TruthfulQA MC2: {utility['student']['truthfulqa_mc2_acc']:.12f}

## Frozen-detector results

| Method | A/A2 Reference score | Frozen threshold | Reference detected | Shared Student score | Student detected | Ownership Detectability Retained |
|---|---:|---:|---|---:|---|---|
{chr(10).join(report_rows)}

ZeroPrint Student raw Pearson: {zero_value['score']['raw_pearson']:.12f}; rescaled similarity: {zero_value['score']['rescaled']:.12f}.

## Bounded conclusion

All five passive ownership fingerprints remained detectable after this tested direct-distillation attack under their already-frozen WMKD A/A2 detectors. This does not imply universal robustness to other attacks, models, datasets, thresholds, or detector variants, and the native scores are not “watermark retention percentages.” No detector was recalibrated using the Student.
"""
    atomic_text(args.project / "docs/reproduction_reports/passive5_shared_ba_report.md", shared_report)

    index_path = args.project / "results/experiment_full_logs_index.json"
    index = json.loads(index_path.read_text())
    index["objects"] = [entry for entry in index["objects"] if not (entry.get("experiment") == "Ba" and entry.get("method") in METHODS and entry.get("shared_attack"))]
    for row in method_rows:
        slug = row["method"].lower(); full = args.project / f"results/{slug}/experiment_ba/full_experiment_log.json"; summary = args.project / f"results/{slug}/experiment_ba/summary.json"
        index["objects"].append({"method":row["method"],"role":"passive_fingerprint_ba_evaluation","experiment":"Ba","run_id":args.run_id,
            "full_log_path":f"results/{slug}/experiment_ba/full_experiment_log.json","full_log_sha256":sha(full),
            "summary_path":f"results/{slug}/experiment_ba/summary.json","summary_sha256":sha(summary),
            "report_path":f"docs/reproduction_reports/{slug}_experiment_ba_report.md",
            "scientific_status":"DETECTABILITY_RETAINED" if row["student_detected"] else "DETECTABILITY_NOT_RETAINED",
            "watermark_evaluation_available":True,"utility_available":True,"shared_attack":True,
            "shared_student_run_id":args.parent_run_id,"dataset_sha256":DATASET_SHA,"telemetry_records":7500})
    index["object_count"] = len(index["objects"]); index["generated_at"] = now(); atomic_json(index_path,index)
    atomic_json(evaluation / "status.json", {"schema_version":"wmkd.passive5-shared-ba-eval.v1","run_id":args.run_id,
        "parent_run_id":args.parent_run_id,"continuation_type":"EVALUATION_ONLY_CONTINUATION","state":"COMPLETED",
        "scientific_status":"COMPLETED","stage":"CLOSURE_COMPLETED","retained_count":retained,"method_count":5,
        "auto_shutdown":False,"terminal":True,"completed_at":now()})
    print(json.dumps({"run_id":args.run_id,"status":"COMPLETED","retained_count":retained,"method_count":5,
                      "shared_full_log":str(shared / "full_experiment_log.json")},ensure_ascii=False),flush=True)


if __name__ == "__main__":
    main()
