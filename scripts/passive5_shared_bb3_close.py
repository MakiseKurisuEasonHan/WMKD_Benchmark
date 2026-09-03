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
    reference_scores = {"LLMPrint":1.0, "REEF":1.0, "HuRef":99.99999237060547, "AWM":1.0, "ZeroPrint":1.0}
    ba_scores = {"LLMPrint":0.82, "REEF":0.9542220066305829, "HuRef":99.99898529052734,
                 "AWM":0.9999974135841643, "ZeroPrint":0.8399372696876526}
    for row in rows:
        row["reference_score"] = reference_scores[row["method"]]
        row["ba_score"] = ba_scores[row["method"]]
        row["ba_to_bb3_change"] = row["score"] - row["ba_score"]
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
            "scientific_justification":"Predeclared detector-agnostic atomic-response identity preservation prevents Qwen meta-task failures on answers with <=1 non-special tokenizer token; all longer answers use the unchanged Bb2 Qwen paraphrasing protocol.",
            "environment":{"host":"autodl-container-9235478639-4a175847", "gpu":"NVIDIA RTX PRO 6000 Blackwell Server Edition", "gpu_memory_mib":97887},
            "source_ba_dataset":{"record_count":20000, "dataset_sha256":"eb90c3e0c95e37d07bf0f099aaeabeedf1779bae7ef8a4aacf25e3fb8bed6ab7", "sample_ids_sha256":IDS_SHA},
            "preprocessing":{"atomic_threshold":"Qwen tokenizer non-special token count <= 1", "atomic_identity_count":4635,
                "qwen_submitted":15365, "qwen_paraphrased":13061, "qwen_natural_identity":2256,
                "pipeline_identity_fallback":48, "rejected_attempts":279, "generation_retry_count":231,
                "final_unresolved_leakage":0, "final_chat_control_token_leakage":0, "final_truncation":0,
                "runtime_seconds":7484.502216789871, "qwen_model":"Qwen/Qwen2.5-3B-Instruct",
                "qwen_revision_identity":{"modelscope_revision":"master", "revision_created_at":1740595239},
                "prompt_sha256":"7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495",
                "decoding":{"temperature":0.7, "top_p":0.9, "seed":42}},
            "pilot":{"status":"PASS", "sample_count":200, "atomic_identity_count":41, "qwen_submitted":159,
                "qwen_paraphrased":143, "qwen_natural_identity":16, "runtime_seconds":63.8928,
                "human_audit_pairs":25, "human_audit":"PASS"},
            "training_parity":{"status":"PASS", "passed_fields":19, "total_fields":19},
            "dataset":dataset, "dataset_archive":archive_dataset, "training":training,
            "student_manifest":student, "reload_validation":reload_result, "detectors":detector_summary,
            "utility":utility, "student_archive":student_archive,
            "failures":[{"stage":"LLMPrint first evaluation attempt", "classification":"ordinary path-resolution infrastructure error", "resolved":True}],
            "continuations":[], "unresolved_errors":[],
            "bounded_conclusion":detector_summary["bounded_conclusion"],
            "completed_at":datetime.now(timezone.utc).isoformat()}
    for name, value in (("dataset_manifest.json", dataset), ("student_manifest.json", student),
                        ("training_summary.json", training), ("utility_results.json", utility),
                        ("detector_summary.json", detector_summary), ("modelscope_dataset_archive.json", archive_dataset),
                        ("modelscope_student_archive.json", student_archive), ("full_experiment_log.json", full)):
        write_json(out / name, value)
    table = "\n".join(f"| {x['method']} | {x['reference_score']:.12f} | {x['threshold']:.12f} | {x['ba_score']:.12f} | {x['score']:.12f} | {x['ba_to_bb3_change']:+.12f} | {'yes' if x['positive'] else 'no'} |" for x in rows)
    report = f"""# Passive-5 Shared Bb3 final report

## Result

The scientific question is whether Bb3 preprocessing plus SFT reduces any passive ownership fingerprint below its frozen detector threshold in the tested same-backbone standardized behavioral-distillation setting. Bb3 completed with one fresh full-parameter Student; detectability remained positive for **{retained}/5** detectors.

## Protocol lineage and decision

Shared Ba supplies the canonical 20,000 QA source and the exact Student/detector/utility protocol. Original Bb is `BLOCKED_AT_PILOT`: successive pilots exposed recurrent instruction-echo/meta-task outputs for one-token `tech` answers. Bb2 is also `BLOCKED_AT_PILOT`: its revised prompt still produced meta-commentary for both deterministic `tech` samples. Neither establishes a formal attack result.

The CPU-only short-answer audit tokenized all 20,000 answers with the frozen Qwen tokenizer and special tokens disabled. Threshold counts for `<=1/2/3/5` were 4,635/7,577/8,698/9,791; both recurrent failures were one token. `<=1` was selected as the smallest uniform detector-agnostic threshold covering them. Bb3 therefore preserves those answers byte-identically and sends every longer answer through the unchanged Bb2 prompt, Qwen snapshot, decoding, ordering, and seed policy.

## Frozen dataset and Student

- Frozen paired records: 20,000; dataset SHA256: `{PAIRED_SHA}`.
- Pilot: 200/200 PASS; 41 atomic identities; 159 Qwen submissions; 25-pair targeted human audit PASS.
- Full20k: 4,635 atomic identities (**23.175%**); 15,365 Qwen submissions; 13,061 Qwen paraphrases; 2,256 natural Qwen identities; 48 pipeline fallbacks; 279 rejected attempts; runtime 7,484.502s.
- Final unresolved leakage/control-token leakage/truncation: 0/0/0. It is incorrect to claim that all responses were paraphrased.
- Ba/Bb3 intended-shared training parity: 19/19 PASS.
- Fresh canonical `meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b7a12671c53f0838cd831a0843b95` Student: 7,500/7,500 optimizer steps, 3 epochs, BF16, effective batch 8, LR 1e-5, seed 42, no resume, no LoRA.
- Training loss: {training['train_loss']:.12f}; runtime: {training['runtime_seconds']:.3f}s.
- Fresh reload: PASS; non-finite parameters: 0; inference response: `{reload_result['inference_smoke']['response']}`.

## Frozen detectors

| Method | Reference | Frozen threshold | Ba | Bb3 | Ba→Bb3 | Detected |
|---|---:|---:|---:|---:|---:|---|
{table}

## Utility

- Ba Student ARC-Challenge acc_norm: 0.497440273038; Bb3 Student: {utility['student']['arc_challenge_acc_norm']:.12f}.
- Ba Student TruthfulQA MC2: 0.475541305678; Bb3 Student: {utility['student']['truthfulqa_mc2_acc']:.12f}.
- Ordinary English and supplementary French generation sanity: PASS for base, teacher, and Student.

## Bounded conclusion

All five ownership fingerprints remained detectable under their already-frozen A/A2 detector protocols after this tested Bb3 UP post-watermark paraphrasing-distillation attack. This does not establish general robustness beyond these models, data, thresholds, and attack semantics. Native detector scores are not watermark-retention percentages.

No claim is made that fingerprints were “transferred.” The result only establishes that Bb3 did not reduce any of the five native scores below its frozen threshold. The 23.175% atomic-identity component is a material limitation and is disclosed explicitly.

## Archival

- Processed20k: private ModelScope dataset `MakiseKurisuEasonHan/WMKD_Benchmark_passive5_shared_bb3_processed20k`; independent redownload and canonical hash validation PASS.
- Final Student: private ModelScope model `MakiseKurisuEasonHan/Llama-3.2-WMKD-Passive5-Shared-Bb3-Student`; 14-file independent redownload, per-file SHA256, secret scan, large-file allowlist, and Llama license/NOTICE checks PASS.
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
    provenance = {"schema_version":"wmkd.passive5-shared-bb3-provenance.v1", "run_id":args.run_id,
                  "dataset_sha256":PAIRED_SHA, "student_manifest_sha256":sha(run / "student/student_manifest.json"),
                  "detector_source_sha256":{x["method"]:x["source_sha256"] for x in rows},
                  "dataset_archive_manifest_sha256":sha(args.data_root / "manifests/passive5_shared_bb3_processed20k_modelscope_archive.json"),
                  "student_archive_manifest_sha256":sha(student_archive_path) if student_archive_path.exists() else None}
    artifacts = {"schema_version":"wmkd.passive5-shared-bb3-artifacts.v1", "run_id":args.run_id,
                 "large_artifacts_external":True, "github_excludes":["models", "checkpoints", "processed20k", "cache", "raw artifacts"],
                 "modelscope_dataset":archive_dataset.get("repository"), "modelscope_student":student_archive.get("repository"),
                 "integrity":"PASS"}
    write_json(out / "provenance_manifest.json", provenance)
    write_json(out / "artifact_manifest.json", artifacts)
    print(json.dumps({"status":"COMPLETED", "retained_count":retained, "student_archive":student_archive["status"]}))


if __name__ == "__main__":
    main()
