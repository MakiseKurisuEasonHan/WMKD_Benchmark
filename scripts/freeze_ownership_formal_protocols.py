"""Freeze authorized REEF/AWM/HuRef/ZeroPrint formal protocols before results exist."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
NEGATIVES = [
    {"slot": 1, "family": "Gemma", "model_id": "google/gemma-2b", "modelscope_id": "google/gemma-2b", "modelscope_weight_revision": "4c0ad9bd274f4fda9be830b72a0833fb1f74a12e"},
    {"slot": 2, "family": "Qwen2", "model_id": "Qwen/Qwen2.5-3B-Instruct", "modelscope_id": "Qwen/Qwen2.5-3B-Instruct", "modelscope_weight_revision": "8f4992eda43eea7c770690ddc0de8f732da246f5"},
    {"slot": 3, "family": "Phi3", "model_id": "microsoft/Phi-3-mini-128k-instruct", "modelscope_id": "microsoft/Phi-3-mini-128k-instruct", "modelscope_weight_revision": "36dd6bdc2b730342af51ce16740601d6471e73ff"},
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def freeze_truthfulqa(data_cache: Path, output: Path) -> dict:
    from datasets import load_dataset
    dataset = load_dataset("truthful_qa", "multiple_choice", split="validation", cache_dir=str(data_cache))
    rows = []
    for index in range(200):
        question = dataset[index]["question"]
        rows.append({"probe_index": index, "source_index": index, "text": question,
                     "text_sha256": hashlib.sha256(question.encode()).hexdigest()})
    payload = {
        "schema_version": "wmkd.reef-truthfulqa-probes.v1", "status": "FROZEN",
        "source": "truthful_qa/multiple_choice validation", "selection": "first 200 rows in cached source order",
        "row_count": 200, "ordered_rows_sha256": canonical_sha(rows), "rows": rows,
    }
    atomic_json(output, payload)
    return payload


def freeze_humaneval(parquet: Path, output: Path) -> dict:
    import pyarrow.parquet as pq
    table = pq.read_table(parquet)
    records = table.to_pylist()
    rows = []
    for index in range(2):
        row = records[index]
        frozen = {"query_index": index, "source_index": index, "task_id": row["task_id"], "prompt": row["prompt"]}
        frozen["row_sha256"] = canonical_sha(frozen)
        rows.append(frozen)
    payload = {
        "schema_version": "wmkd.zeroprint-humaneval-queries.v1", "status": "FROZEN",
        "source": "ModelScope opencompass/humaneval openai_humaneval/test", "source_parquet_sha256": sha256(parquet),
        "selection": "first 2 rows in source order", "row_count": 2,
        "ordered_rows_sha256": canonical_sha(rows), "rows": rows,
    }
    atomic_json(output, payload)
    return payload


def calibration(metric: str, direction: str = "higher") -> dict:
    return {
        "status": "FROZEN_BEFORE_FORMAL_RESULTS", "metric": metric, "score_direction": direction,
        "negative_distribution": "three frozen family-diverse unrelated models, one score per model",
        "threshold_rule": "tau = maximum score among the three frozen unrelated negatives",
        "positive_rule": "suspect score > tau",
        "tie_rule": "score equal to tau is negative",
        "rationale": "pre-registered empirical family-wise separation boundary; no arbitrary numerical constant and no post-result tuning",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    args = parser.parse_args()
    protocols = args.project / "results" / "ownership_protocols"
    negative_manifest = {
        "schema_version": "wmkd.ownership-shared-negative-panel.v1", "status": "FROZEN",
        "selection_time": "before formal method results", "slot_count": 3,
        "family_diverse": True, "replacement_allowed": False, "models": NEGATIVES,
        "ordered_panel_sha256": canonical_sha(NEGATIVES),
    }
    atomic_json(protocols / "shared_negative_panel_3.json", negative_manifest)
    truth = freeze_truthfulqa(args.data_root / "cache" / "datasets", protocols / "reef_truthfulqa_200.json")
    humaneval_path = args.data_root / "datasets" / "ownership" / "humaneval" / "openai_humaneval" / "test-00000-of-00001.parquet"
    human = freeze_humaneval(humaneval_path, protocols / "zeroprint_humaneval_2.json")
    huref_tokens = args.data_root / "gates" / "huref" / "sorted_tokens_4096.json"
    huref_gate = args.data_root / "gates" / "huref" / "scaling_gate_direct_full.json"
    if sha256(huref_tokens) != "a4f3f05c8cad5bb395bd6ca7202a2efcb3760c582f041013d071b2d637679d69":
        raise RuntimeError("HuRef frozen token manifest SHA mismatch")
    if json.loads(huref_gate.read_text())["status"] != "COMPLETED":
        raise RuntimeError("HuRef K=4096 direct gate is not complete")

    shared = {"path": "results/ownership_protocols/shared_negative_panel_3.json",
              "sha256": sha256(protocols / "shared_negative_panel_3.json")}
    specs = {
        "reef": {
            "official_commit": "48329f6f3695a8aea33975832159e7ce44ad73f9",
            "scientific_design": {"probe": "TruthfulQA", "samples": 200, "probe_manifest": "results/ownership_protocols/reef_truthfulqa_200.json",
                                  "probe_manifest_sha256": sha256(protocols / "reef_truthfulqa_200.json"),
                                  "representation": "forward-hook output[0] at last token", "layer": 27,
                                  "metric": "official centered linear CKA on 200xhidden activation matrices"},
            "calibration": calibration("centered_linear_CKA"),
        },
        "awm": {
            "official_commit": "bc20ff8e63cec57f5da422ae065686ced275e76d",
            "scientific_design": {"primary_representation": "attention q_proj.weight and k_proj.weight",
                                  "dimension_alignment": "official overlapping-vocabulary embedding LAP with absolute-cosine cost and sign correction",
                                  "layer_alignment": "official LAP when layer counts differ; identity order when equal",
                                  "per_layer_metrics": ["unbiased_linear_CKA(Wq.T)", "unbiased_linear_CKA(Wk.T)"],
                                  "primary_score": "arithmetic mean of Wq and Wk CKA over all official matched layer pairs",
                                  "score_key": "Wq_Wk_weights"},
            "calibration": calibration("official_mean_Wq_Wk_unbiased_linear_CKA"),
            "supplementary_release_reference": {"negative_pair_mean": 0.00375, "negative_pair_std": 0.0028,
                                                 "status": "reported_only_not_controlling_due_source_comment_std_not_specified"},
        },
        "huref": {
            "official_commit": "9c34548a6f6c1e78780e1fd07de56c7a3357f6ef",
            "scientific_design": {"experiment": "A", "selected_tokens": 4096,
                                  "token_manifest": str(huref_tokens), "token_manifest_sha256": sha256(huref_tokens),
                                  "layers": [26, 27], "invariant_terms": ["WqWk", "WvWo", "WuWd"],
                                  "gqa_mapping": "repeat_interleave KV heads to query-head dimension",
                                  "feature_extract_method": "official Mean_pooling", "metric": "official ICS = 100*cosine_similarity of standardized flattened features",
                                  "scaling_gate": str(huref_gate), "scaling_gate_sha256": sha256(huref_gate)},
            "calibration": calibration("ICS_percent"),
        },
        "zeroprint": {
            "official_commit": "16a02aa4cfd5693ecfa757e9d2832b7e9babada0c",
            "scientific_design": {"dataset": "ModelScope opencompass/humaneval", "query_count": 2,
                                  "query_manifest": "results/ownership_protocols/zeroprint_humaneval_2.json",
                                  "query_manifest_sha256": sha256(protocols / "zeroprint_humaneval_2.json"),
                                  "perturbations_per_query": 4, "repeats": 20, "continuation_word_limit": 20,
                                  "generation": {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9, "top_k": 50, "do_sample": True, "max_input_length": 512},
                                  "perturbation": {"method": "official GloVe word substitution", "k_words_to_replace": 3, "top_m_neighbors": 10,
                                                   "embedding": "canonical Stanford GloVe 6B 100d safe reconstruction"},
                                  "output_embedding": "sentence-transformers/all-mpnet-base-v2",
                                  "gradient": "official ridge-regression Jacobian, alpha=0.001",
                                  "aggregation": "mean", "similarity": "official correlation rescaled from [-1,1] to [0,1]"},
            "calibration": calibration("rescaled_Pearson_correlation"),
            "runtime_gate": {"status": "PENDING", "rule": "use 5 negatives iff Reference+5 <=5h; else use 3 iff Reference+3 <=5h; never reduce 2x4x20 core budget"},
        },
    }
    for method, spec in specs.items():
        payload = {
            "schema_version": f"wmkd.{method}-formal-protocol.v1", "method": method, "experiment": "A",
            "status": "READY_FOR_FORMAL" if method != "zeroprint" else "NEEDS_RUNTIME_GATE",
            "formal_authorized": method != "zeroprint", "frozen_before_results": True,
            "canonical_reference": {"model_id": "meta-llama/Llama-3.2-3B-Instruct", "revision": REVISION, "model_modified": False},
            "official_commit": spec["official_commit"], "negative_panel": shared, **{k: v for k, v in spec.items() if k != "official_commit"},
        }
        payload["protocol_content_sha256"] = canonical_sha(payload)
        atomic_json(protocols / f"{method}_formal_protocol.json", payload)
        config = {
            "method": method.upper() if method != "zeroprint" else "ZeroPrint", "experiment": "A",
            "status": payload["status"], "formal_authorized": payload["formal_authorized"],
            "reference": payload["canonical_reference"], "official": {"commit": spec["official_commit"]},
            "protocol_manifest": {"path": f"results/ownership_protocols/{method}_formal_protocol.json",
                                  "sha256": sha256(protocols / f"{method}_formal_protocol.json")},
            "hard_wall_clock_hours": 5, "ba_authorized": False,
        }
        atomic_json(args.project / "configs" / "watermark" / f"{method}_experiment_a.yaml", config)
    # Correct the earlier REEF terminalization without erasing its audit history in Git.
    reef_summary = args.project / "results" / "reef" / "experiment_a" / "summary.json"
    old = json.loads(reef_summary.read_text(encoding="utf-8"))
    old.update(status="READY_FOR_FORMAL", terminal=False, formal_result=None, preferred_fingerprint=None,
               ba_ready=False, reclassification="prior BLOCKED was authorization/protocol infrastructure misclassification; no formal science had started",
               protocol_manifest="results/ownership_protocols/reef_formal_protocol.json")
    old.pop("blocker", None)
    atomic_json(reef_summary, old)
    state = {
        "schema_version": "wmkd.ownership-pipeline-state.v2", "state_machine": ["PENDING", "NEEDS_PROTOCOL_FREEZE", "READY_FOR_FORMAL", "RUNNING", "EVALUATING", "CLOSING", "terminal"],
        "llmprint": "BLOCKED_RESOURCE_PROVENANCE", "reef": "READY_FOR_FORMAL", "awm": "READY_FOR_FORMAL",
        "huref": "READY_FOR_FORMAL", "zeroprint": "NEEDS_RUNTIME_GATE", "ba": "NOT_STARTED",
        "updated_at": now(),
    }
    atomic_json(args.project / "results" / "ownership_pipeline_state.json", state)


if __name__ == "__main__":
    main()
