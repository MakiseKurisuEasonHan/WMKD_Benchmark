"""Records-only final closure for SCW A2; never runs scientific workloads."""
from __future__ import annotations

import json
from pathlib import Path

P = Path("/root/autodl-tmp/WMKD_Benchmark")
D = Path("/root/autodl-tmp/WMKD_Benchmark_data")
RUN = D / "runs/scw/a2_eval_cont2/scw_a2_eval_cont2_20260901_021640"
RESULT = P / "results/scw/experiment_a2"
TEACHER = D / "runs/scw/a2/scw_a2_20260831_214339/models/Llama-3.2-3B-Instruct_scw_a2_20260831_214339_French_WMKD_SCW_A"
MARKER = "SCW_A2_FINAL_CLOSURE_CONT3_20260901"


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_once(path: Path, text: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if MARKER not in current:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(current.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def main() -> None:
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    if summary["detector"]["base"]["primary"]["p_value"] != 0.9199569225311279:
        raise RuntimeError("Base detector provenance mismatch")
    if summary["detector"]["teacher"]["primary"]["p_value"] != 0.0:
        raise RuntimeError("Teacher detector provenance mismatch")
    summary.update({
        "status": "COMPLETED",
        "scientific_status": "REPRODUCTION_SUCCESSFUL",
        "training_status": "COMPLETED",
        "evaluation_cont1": "FAILED_AT_BASE_DETECTOR",
        "evaluation_cont2": "COMPLETED",
        "report_summary_cont3": "COMPLETED",
        "preferred_teacher": "YES",
        "preferred_teacher_bool": True,
        "training_metrics": {
            "optimizer_steps": 2500, "exit_code": 0, "train_end": True,
            "duration_seconds": 11570.9348, "final_logged_loss": 3.3589,
            "aggregate_train_loss": 5.2890466034,
            "final_learning_rate": 9.7477558e-12, "final_grad_norm": 12.75,
        },
        "strict_a": {"formal_training": "NEVER_STARTED", "scientific_result": "NOT_ESTABLISHED",
                     "classification": "PRE_FORMAL_INFRASTRUCTURE_ATTEMPT"},
        "a2_adaptation": {
            "unique_records": 80000, "formal_exposures": 160000,
            "schedule": "NumPy Generator(PCG64), seed 42, deterministic two-pass replay",
            "role_probabilities": [0.6, 0.2, 0.2], "role_counts": [47773, 16291, 15936],
            "datasets": ["CohereForAI/aya_collection_language_split (French)",
                         "wyj123456/instruct", "mapjack/openwebtextSample"],
        },
        "generation": {"base_records": 1000, "teacher_records": 1000, "errors": 0,
                       "fresh_process_reload": "PASS"},
        "french_eval": {
            "dataset": "jpacifico/French-Alpaca-dataset-Instruct-55K",
            "revision": "c13216a7a935baf62fb81efc56eed1739b222d2f",
            "selection": "source-order 0-999",
            "frozen1000_sha256": "c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d",
            "manifest_sha256": "e178179e8d46bdc8c555f820ca027c5eddf813d3db4b6b0467deb830305e8f28",
        },
        "teacher_artifact": {"path": str(TEACHER), "status": "COMPLETE",
                             "manifest_sha256": "27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b"},
    })
    summary["limitations"] = [
        "not an exact SCW reproduction or full-paper reproduction",
        "strict A official-data attempt never reached Formal training and established no scientific result",
        "A2 used domestically accessible replacement datasets",
        "A2 used an 80k unique pool and deterministic two-pass replay to 160k exposures",
        "cont1 failed before detector science because the runtime tokenizer had no pad token",
        "cont2 reused immutable generations and applied runtime-only EOS-as-PAD with unchanged vocabulary and weights",
    ]
    atomic_json(RESULT / "summary.json", summary)
    atomic_json(RUN / "summary.json", summary)

    curve_b = summary["detector"]["base"]["curve"]
    curve_t = summary["detector"]["teacher"]["curve"]
    curve_rows = "\n".join(
        f"| {b['n_queries']} | {b['p_value']:.10g} | {'fingerprinted' if b['fingerprinted'] else 'negative'} | "
        f"{t['p_value']:.10g} | {'fingerprinted' if t['fingerprinted'] else 'negative'} |"
        for b, t in zip(curve_b, curve_t)
    )
    report = f"""# SCW Experiment A2 Final Report

## 1. Experiment identity and bounded conclusion

SCW A2 is the fifth WMKD watermark-method reproduction on the canonical `Llama-3.2-3B-Instruct` backbone. **SCW core method / idea reproduction successful under the WMKD A2 adapted domestic-data and 80k-unique-pool setting on the canonical Llama-3.2-3B-Instruct backbone.** This is neither an exact SCW reproduction nor a full-paper reproduction.

## 2. Strict A history and why A2 exists

Strict Experiment A targeted the official-data/strict pipeline. Formal training **never started** and no scientific result was established. Its pre-formal infrastructure blockers included Python 3.12 and 3.11 post-`train_end` SIGABRT/PyGILState finalization, PyArrow/streaming lifecycle behavior, Hugging Face metadata endpoint leakage, unstable and non-resumable shard downloads, exact-stream materialization complexity, and CDN throughput instability. These are not a scientific failure of SCW. A2 was created as an explicitly adapted, domestically accessible idea reproduction.

## 3. Paper / Official / A / A2 comparison

| Dimension | Paper / official intent | Strict A | A2 |
|---|---|---|---|
| Data | Official SCW sources | Pinned official identities; access/materialization blocked | Role-equivalent domestic replacements |
| Formal training | Full-parameter SCW | Never started | 2500/2500, exit 0 |
| Stream | Official stochastic pipeline | Exact materialization attempts blocked | Frozen 80k, deterministic two-pass 160k exposures |
| Scientific result | Paper method | Not established | Method/idea reproduction successful |

## 4. A2 datasets and role semantics

Role0 is `CohereForAI/aya_collection_language_split` French (`47,773`, watermark-domain French); Role1 is `wyj123456/instruct` (`16,291`, instruction regularization); Role2 is `mapjack/openwebtextSample` (`15,936`, general-text regularization). Configured probabilities are `0.6 / 0.2 / 0.2`.

## 5. Frozen stream and training configuration

The pool contains 80,000 unique records scheduled by NumPy `Generator(PCG64)` seed 42 and replayed in the identical order twice for exactly 160,000 exposures. Training used full parameters, batch 4, gradient accumulation 16, effective batch 64, sequence length 512, LR `2e-5`, Adafactor, cosine schedule, warmup 0.1, and 2500 optimizer steps.

Environment: Python 3.11, Torch `2.8.0+cu128`, CUDA 12.8 on AutoDL. Official tracked source `eth-sri/robust-llm-fingerprints@15bc1929569357130f2dbc0b09f91bbf4f4bd947` remained unmodified.

## 6. Training result and Teacher

Run `scw_a2_20260831_214339` completed 2500/2500 with `train_end`, exit code 0, in 11,570.9348 seconds (about 3 h 12 m 51 s). Final logged loss was `3.3589`, aggregate train loss `5.2890466034`, final LR `9.7477558e-12`, and final grad norm `12.75`.

Teacher: `{TEACHER}`. Teacher manifest SHA256: `27f68ea443ca1dbc9f02036ac560a12db5cb063ceec589a0144be5586da97b7b`.

## 7. French evaluation provenance and generation

Dataset `jpacifico/French-Alpaca-dataset-Instruct-55K`, revision `c13216a7a935baf62fb81efc56eed1739b222d2f`, source-order 0–999. Frozen1000 SHA256: `c60cd7d03acbd3535c5564eafe521f88179833761924953fa599237c5082a69d`; manifest SHA256: `e178179e8d46bdc8c555f820ca027c5eddf813d3db4b6b0467deb830305e8f28`. Base and Teacher generation each completed 1000/1000 with zero generation errors and fresh-process reload PASS.

## 8. Evaluation continuations and detector infrastructure

Cont1 completed both generation sets but failed at `BASE_DETECTOR` before a scientific detector result because the Llama tokenizer had no pad token. Cont2 made only a runtime **EOS-as-PAD** adapter fix: `padding_side=left`; when absent, `pad_token=eos_token` (`<|eot_id|>`, ID 128009). Vocabulary remained 128256; no token, model weight, completion, tokenizer-on-disk file, alpha, or KGW mathematics changed.

## 9. Primary detector and supplementary curve

At alpha `0.001`, Base primary p=`0.9199569225311279` (negative) and Teacher p=`0.0` (fingerprinted): Teacher positive / Base negative. Fixed permutation seed is 42.

| Queries | Base p | Base | Teacher p | Teacher |
|---:|---:|---|---:|---|
{curve_rows}

The curve is supplementary; the 1000-query point is primary.

## 10. Utility and sanity

ARC Challenge acc_norm Base/Teacher: `0.4505119454 / 0.4488054608` (delta `-0.0017064846`). TruthfulQA MC2 Base/Teacher: `0.5051617516 / 0.5032315125` (delta `-0.0019302391`). Ordinary generation sanity passed for Base and Teacher. Supplementary French sanity passed for Base and Teacher. Utility fresh-process reload passed.

## 11. Preferred Teacher

`preferred_teacher = YES`: Teacher detector positive, Base detector negative, strong and stable 10–1000 query margin, minimal ARC/TruthfulQA deltas, ordinary/French sanity PASS, and fresh reload PASS. Ba was not started.

## 12. Deviations, limitations, and final judgement

Declared deviations are replacement datasets, the 80k frozen unique pool, deterministic PCG64(42) scheduling, and two-pass replay. Strict A and cont1 failure evidence remain preserved. The conclusion is bounded to the tested WMKD A2 setting: SCW's core method/idea reproduced successfully; no claim of exact official-data or full-paper reproduction is made.
"""
    report_path = RESULT / "final_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    (RUN / "formal_report.md").write_text(report, encoding="utf-8")

    legacy = P / "scw_experiment_a_log.md"
    archive = P / "docs/experiment_logs/scw_experiment_a_legacy_root_snapshot.md"
    if legacy.exists() and not archive.exists():
        legacy.replace(archive)

    record = f"""## SCW A2 final closure — report/summary cont3

<!-- {MARKER} -->
Strict A remains a pre-formal infrastructure attempt: Formal training never started and no scientific result was established. A2 run `scw_a2_20260831_214339` completed 2500/2500 and produced the immutable Teacher. Cont1 preserved Base/Teacher 1000-record generations but failed at detector padding infrastructure. Cont2 applied runtime-only left EOS-as-PAD and completed evaluation: Base/Teacher primary p-values `0.9199569225311279 / 0.0`, ARC `0.4505119454 / 0.4488054608`, TruthfulQA MC2 `0.5051617516 / 0.5032315125`, ordinary/French sanity PASS/PASS, and preferred Teacher **YES**. The bounded conclusion is successful SCW core method/idea reproduction under the adapted domestic-data, 80k-pool, deterministic two-pass A2 setting—not exact or full-paper reproduction. Ba remains NOT STARTED. Next step: separately archive the final Teacher to ModelScope, verify the archive, then discuss Ba without starting it automatically.
"""
    for rel in ("PROJECT_STATUS.md", "TODO.md", "DECISIONS.md", "EXPERIMENT_LOG.md", "CODEX_LOG.md",
                "docs/experiment_logs/scw_experiment_a_log.md"):
        append_once(P / rel, record)

    closure = {"status": "COMPLETE", "continuation": "cont3", "scientific_work_rerun": False,
               "report": str(report_path), "summary": str(RESULT / "summary.json"),
               "project_records_updated": True, "preferred_teacher": "YES",
               "auto_shutdown_enabled": False, "ba_started": False}
    atomic_json(RESULT / "closure_cont3.json", closure)


if __name__ == "__main__":
    main()
