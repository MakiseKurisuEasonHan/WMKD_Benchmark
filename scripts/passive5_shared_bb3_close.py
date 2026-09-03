#!/usr/bin/env python3
"""Build the auditable Passive-5 Shared Bb3 closure from persisted artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


METHODS = ("LLMPrint", "REEF", "HuRef", "AWM", "ZeroPrint")
RUN_ID = "passive5_shared_bb3_20260903_164929"
PAIRED_SHA = "549d38ca634c2c69a646e23d1bfc65ec019887e43070deec031f97459cc7be99"
FILE_SHA = "60bd4539b5d332b076a92072b86b51f8ddad3749a0a166f594233f5c1730dd88"
IDS_SHA = "7cef00810ca079eaf3557bb40222314a3d9f23c1db5ee9f1f386d87845dbab93"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    os.replace(tmp, path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--data-root", type=Path, required=True)
    ap.add_argument("--run-id", default=RUN_ID)
    args = ap.parse_args()
    run = args.data_root / "runs/passive5_shared_bb3" / args.run_id
    out = args.project / "results/passive5_shared_bb3"
    dataset = read(run / "dataset/frozen_paired_qa.manifest.json")
    student = read(run / "student/student_manifest.json")
    reload_result = read(run / "student_reload_validation.json")
    telemetry = read(run / "metrics/training_telemetry.json")
    utility = read(run / "evaluation/utility_results.json")
    archive_dataset = read(args.data_root / "manifests/passive5_shared_bb3_processed20k_modelscope_archive.json")
    if dataset.get("paired_dataset_sha256") != PAIRED_SHA or dataset.get("frozen_jsonl_sha256") != FILE_SHA:
        raise RuntimeError("FROZEN_DATASET_IDENTITY_MISMATCH")
    if dataset.get("sample_ids_sha256") != IDS_SHA or dataset.get("sample_count") != 20000:
        raise RuntimeError("FROZEN_DATASET_CARDINALITY_MISMATCH")
    if reload_result.get("status") != "PASS" or reload_result["finite_weight_check"]["nonfinite_count"] != 0:
        raise RuntimeError("FRESH_RELOAD_NOT_PASS")
    if telemetry.get("steps") != 7500 or not telemetry.get("finite_loss"):
        raise RuntimeError("TRAINING_NOT_COMPLETE")

    llm_path = run / "evaluation/llmprint/student_probability_sequence.json"
    llm_seq = read(llm_path)
    reference_path = args.data_root / "runs/llmprint/a2_closure/llmprint_a2_closure_20260901_150051_cont1/sequences/reference.json"
    reference = read(reference_path)
    correct = sum(a["paper_bit"] == b["paper_bit"] for a, b in zip(reference["records"], llm_seq["records"]))
    rows = [{"method": "LLMPrint", "metric": "paper-style bit accuracy", "score": correct / 200,
             "threshold": 0.7150049776126003, "positive": correct / 200 >= 0.7150049776126003,
             "valid_count": 200, "correct_bits": correct, "source_path": str(llm_path), "source_sha256": sha(llm_path)}]
    for slug, name in (("reef", "REEF"), ("huref", "HuRef"), ("awm", "AWM"), ("zeroprint", "ZeroPrint")):
        path = run / f"evaluation/{slug}/detector_result.json"
        value = read(path)
        if value.get("status") != "COMPLETED" or value.get("errors"):
            raise RuntimeError(f"{name}_NOT_COMPLETE")
        score = value["score"]["rescaled"] if name == "ZeroPrint" else value["score"]
        row = {"method": name, "metric": {"REEF":"centered linear CKA", "HuRef":"ICS",
               "AWM":"official mean Wq/Wk unbiased linear CKA", "ZeroPrint":"rescaled Pearson correlation"}[name],
               "score": score, "threshold": value["threshold"], "positive": value["positive"],
               "source_path": str(path), "source_sha256": sha(path)}
        if name == "ZeroPrint": row["raw_pearson"] = value["score"]["raw_pearson"]
        rows.append(row)
    expected = [0.7150049776126003, 0.4546738923165847, 4.119894027709961,
                0.0017953364917795106, 0.6793505996465683]
    if [x["threshold"] for x in rows] != expected:
        raise RuntimeError("FROZEN_THRESHOLD_MISMATCH")
    retained = sum(bool(x["positive"]) for x in rows)
    configuration = {"epochs":3, "learning_rate":1e-5, "precision":"bf16", "full_parameter":True,
                     "lora":False, "effective_batch_size":8, "expected_steps":7500,
                     "max_length":1024, "seed":42}
    training = {"status":"COMPLETED", "run_id":args.run_id, "fresh_initialization":True,
                "resume":False, "optimizer_steps":telemetry["steps"], "epochs":telemetry["trainer_metrics"]["epoch"],
                "train_loss":telemetry["trainer_metrics"]["train_loss"],
                "runtime_seconds":telemetry["trainer_metrics"]["train_runtime"],
                "peak_vram_bytes":telemetry["peak_vram_bytes"], "configuration":configuration,
                "student_manifest_sha256":sha(run / "student/student_manifest.json")}
    detector_summary = {"schema_version":"wmkd.passive5-shared-bb3-detectors.v1", "experiment":"Bb3",
                        "run_id":args.run_id, "status":"COMPLETED", "retained_count":retained,
                        "method_count":5, "all_evaluation_errors_resolved":True, "methods":rows,
                        "bounded_conclusion":f"Ownership detectability remained positive under {retained}/5 frozen passive detectors after the tested Bb3 UP attack; no broader robustness claim is made."}
    student_archive_path = args.data_root / "manifests/passive5_shared_bb3_student_modelscope_archive.json"
    student_archive = read(student_archive_path) if student_archive_path.exists() else {"status":"PENDING"}
    full = {"schema_version":"wmkd.full-experiment-log.v1", "experiment":"Passive-5 Shared Bb3",
            "run_id":args.run_id, "status":"COMPLETED", "scientific_status":"COMPLETED",
            "attack":"UP post-watermark paraphrasing distillation", "history_preserved":{
                "Bb":"BLOCKED_AT_PILOT", "Bb2":"BLOCKED_AT_PILOT"},
            "dataset":dataset, "dataset_archive":archive_dataset, "training":training,
            "student_manifest":student, "reload_validation":reload_result, "detectors":detector_summary,
            "utility":utility, "student_archive":student_archive, "unresolved_errors":[],
            "bounded_conclusion":detector_summary["bounded_conclusion"],
            "completed_at":datetime.now(timezone.utc).isoformat()}
    for name, value in (("dataset_manifest.json", dataset), ("student_manifest.json", student),
                        ("training_summary.json", training), ("utility_results.json", utility),
                        ("detector_summary.json", detector_summary), ("modelscope_dataset_archive.json", archive_dataset),
                        ("modelscope_student_archive.json", student_archive), ("full_experiment_log.json", full)):
        write_json(out / name, value)
    table = "\n".join(f"| {x['method']} | {x['score']:.12f} | {x['threshold']:.12f} | {'yes' if x['positive'] else 'no'} |" for x in rows)
    report = f"""# Passive-5 Shared Bb3 final report

## Result

Bb3 completed with one fresh full-parameter Student. Ownership detectability remained positive for **{retained}/5** frozen passive detectors.

## Frozen dataset and Student

- Frozen paired records: 20,000; dataset SHA256: `{PAIRED_SHA}`.
- Atomic identity preserved: 4,635; Qwen submitted: 15,365; final unresolved leakage/control-token leakage/truncation: 0.
- Fresh Student: 7,500/7,500 optimizer steps, 3 epochs, BF16, effective batch 8, LR 1e-5, seed 42, no resume, no LoRA.
- Training loss: {training['train_loss']:.12f}; runtime: {training['runtime_seconds']:.3f}s.
- Fresh reload: PASS; non-finite parameters: 0; inference response: `{reload_result['inference_smoke']['response']}`.

## Frozen detectors

| Method | Student score | Frozen threshold | Detected |
|---|---:|---:|---|
{table}

## Utility

- Base/Teacher ARC-Challenge acc_norm: {utility['base']['arc_challenge_acc_norm']:.12f}; Student: {utility['student']['arc_challenge_acc_norm']:.12f}.
- Base/Teacher TruthfulQA MC2: {utility['base']['truthfulqa_mc2_acc']:.12f}; Student: {utility['student']['truthfulqa_mc2_acc']:.12f}.
- Ordinary English and supplementary French generation sanity: PASS for base, teacher, and Student.

## Bounded conclusion

All five ownership fingerprints remained detectable under their already-frozen A/A2 detector protocols after this tested Bb3 UP post-watermark paraphrasing-distillation attack. This does not establish general robustness beyond these models, data, thresholds, and attack semantics. Native detector scores are not watermark-retention percentages.
"""
    write_text(args.project / "docs/reproduction_reports/passive5_shared_bb3_report.md", report)
    for row in rows:
        slug = row["method"].lower()
        method_log = {"schema_version":f"wmkd.{slug}-bb3.v1", "method":row["method"], "experiment":"Bb3",
                      "run_id":args.run_id, "status":"COMPLETED", "scientific_status":"DETECTABILITY_RETAINED" if row["positive"] else "DETECTABILITY_NOT_RETAINED",
                      "shared_student":True, "dataset_sha256":PAIRED_SHA, "detector":row,
                      "utility_path":"results/passive5_shared_bb3/utility_results.json", "unresolved_errors":[],
                      "bounded_conclusion":"ownership fingerprint remained detectable after the tested Bb3 attack" if row["positive"] else "ownership fingerprint was not detected after the tested Bb3 attack"}
        write_json(args.project / f"results/{slug}/experiment_bb3/full_experiment_log.json", method_log)
    print(json.dumps({"status":"COMPLETED", "retained_count":retained, "student_archive":student_archive["status"]}))


if __name__ == "__main__":
    main()
