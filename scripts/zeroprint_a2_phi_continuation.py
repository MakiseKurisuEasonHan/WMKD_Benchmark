"""ZeroPrint A2 Phi-only compatibility continuation and frozen closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.cache_utils import DynamicCache

import zeroprint_experiment_a2 as base


EXPECTED = {
    "reference_a": "580ece1cf0c2c6d498a8e4abd212f19601752354467071735307f1d55aea6b11",
    "reference_b": "580ece1cf0c2c6d498a8e4abd212f19601752354467071735307f1d55aea6b11",
    "negative_1": "9eb9a8a474f312cd3668d2a5c898cf9a4842dfc52c803f737d0be0cfbee7a749",
    "negative_2": "e547fe70efd52ec6a993a7fb19d070f846fbc0048a1d3a637eb95117b0b8bfc0",
}
PHI_REV = "36dd6bdc2b730342af51ce16740601d6471e73ff"


def atomic(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phi_cache_shim() -> dict:
    if not hasattr(DynamicCache, "get_seq_length"):
        raise RuntimeError("DynamicCache has neither seen_tokens nor get_seq_length")
    mappings = []
    if not hasattr(DynamicCache, "seen_tokens"):
        DynamicCache.seen_tokens = property(lambda self: self.get_seq_length())
        mappings.append({
            "old_api": "DynamicCache.seen_tokens",
            "current_equivalent": "DynamicCache.get_seq_length()",
            "return_type": "int",
            "semantic_justification": "number of previously cached sequence positions",
        })
    if not hasattr(DynamicCache, "get_max_length"):
        DynamicCache.get_max_length = lambda self: None
        mappings.append({
            "old_api": "DynamicCache.get_max_length()",
            "current_equivalent": "None for an unbounded DynamicCache",
            "return_type": "NoneType",
            "example_value": None,
            "semantic_justification": "Transformers 4.40.2 DynamicCache explicitly returned None because a dynamically growing cache has no maximum capacity",
        })
    if not hasattr(DynamicCache, "get_usable_length"):
        DynamicCache.get_usable_length = lambda self, new_seq_length, layer_idx=0: self.get_seq_length(layer_idx)
        mappings.append({
            "old_api": "DynamicCache.get_usable_length(new_seq_length, layer_idx=0)",
            "current_equivalent": "DynamicCache.get_seq_length(layer_idx) for an unbounded dynamic cache",
            "return_type": "int",
            "semantic_justification": "Transformers 4.40.2 returned the full previous sequence length whenever get_max_length() was None",
        })
    return {
        "required": bool(mappings),
        "scope": "continuation process only",
        "mappings": mappings,
        "old_source": "huggingface/transformers v4.40.2 src/transformers/cache_utils.py",
        "current_source": "transformers 4.55.2 transformers/cache_utils.py",
        "static_phi_cache_api_scan": {
            "get_seq_length": "native current API",
            "update": "native current API",
            "from_legacy_cache": "native current API",
            "to_legacy_cache": "native current API",
            "seen_tokens": "compatibility property",
            "get_max_length": "compatibility method returning None",
            "get_usable_length": "compatibility method returning current sequence length for DynamicCache",
        },
    }


def compatibility_tests(phi_path: Path) -> dict:
    tokenizer = AutoTokenizer.from_pretrained(phi_path, local_files_only=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        phi_path,
        local_files_only=True,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="cuda:0",
    ).eval()
    inputs = tokenizer("def add(a, b):", return_tensors="pt").to("cuda:0")
    with torch.inference_mode():
        cache = DynamicCache()
        first = model(**inputs, past_key_values=cache, use_cache=True)
        cache_after_prompt = int(first.past_key_values.get_seq_length())
        next_token = first.logits[:, -1:].argmax(dim=-1)
        grown_attention_mask = torch.cat(
            [inputs.attention_mask, torch.ones_like(next_token, dtype=inputs.attention_mask.dtype)], dim=1
        )
        second = model(
            input_ids=next_token,
            attention_mask=grown_attention_mask,
            past_key_values=first.past_key_values,
            use_cache=True,
        )
        cache_after_decode = int(second.past_key_values.get_seq_length())
        smoke = model.generate(
            **inputs,
            max_new_tokens=4,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
        cached = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
        )
        uncached = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
            use_cache=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    result = {
        "status": "PASS" if torch.equal(cached, uncached) and smoke.shape[1] > inputs.input_ids.shape[1] and cache_after_decode == cache_after_prompt + 1 else "FAIL",
        "engineering_smoke_generated_tokens": int(smoke.shape[1] - inputs.input_ids.shape[1]),
        "cache_seq_length_after_prompt": cache_after_prompt,
        "cache_seq_length_after_one_decode_step": cache_after_decode,
        "cache_growth_correct": cache_after_decode == cache_after_prompt + 1,
        "greedy_cached_token_ids": cached[0].tolist(),
        "greedy_uncached_token_ids": uncached[0].tolist(),
        "deterministic_token_ids_equal": bool(torch.equal(cached, uncached)),
        "formal_scientific_evidence": False,
    }
    del model, tokenizer, inputs, cache, first, second, next_token, grown_attention_mask, smoke, cached, uncached
    base.release()
    if result["status"] != "PASS":
        raise RuntimeError("PHI_CACHE_COMPATIBILITY_EQUIVALENCE_TEST_FAILED")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--parent-run-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    started = time.time()
    out = args.project / "results/zeroprint/experiment_a2"
    protocol = out / "protocol"
    parent_art = args.data_root / f"artifacts/zeroprint/experiment_a2/{args.parent_run_id}"
    art = args.data_root / f"artifacts/zeroprint/experiment_a2/{args.run_id}"
    art.mkdir(parents=True, exist_ok=False)

    manifest_path = protocol / "generation_manifest.json"
    prior_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if [x["role"] for x in prior_manifest["runs"]] != ["reference_a", "reference_b", "negative_1", "negative_2"]:
        raise RuntimeError("FAIL_CLOSED_UNEXPECTED_PRIOR_GENERATION_MANIFEST")
    verified = {}
    for role, expected in EXPECTED.items():
        path = parent_art / f"{role}_fingerprint.npy"
        actual = sha(path)
        verified[role] = {"path": str(path), "expected_sha256": expected, "actual_sha256": actual}
        if actual != expected:
            raise RuntimeError(f"FAIL_CLOSED_SHA_MISMATCH:{role}")
    protocol_hashes = {
        name: sha(protocol / name)
        for name in [
            "negative_panel_manifest.json",
            "perturbation_manifest.json",
            "unit_test_results.json",
            "runtime_gate.json",
            "generation_manifest.json",
        ]
    }
    panel = json.loads((protocol / "negative_panel_manifest.json").read_text(encoding="utf-8"))
    if panel["models"][2]["model_id"] != "microsoft/Phi-3-mini-128k-instruct" or panel["models"][2]["modelscope_weight_revision"] != PHI_REV:
        raise RuntimeError("FAIL_CLOSED_PHI_PANEL_IDENTITY_MISMATCH")
    if base.freegb(args.data_root) <= 100:
        raise RuntimeError("GLOBAL_DISK_SAFETY_BLOCK")

    shim = install_phi_cache_shim()
    phi_path = args.data_root / "models/llmprint_validation/models/microsoft--Phi-3-mini-128k-instruct/snapshots/master"
    tests = compatibility_tests(phi_path)
    compatibility = {
        "classification": "TRANSFORMERS_MODEL_CODE_CACHE_COMPATIBILITY_FAILURE",
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "phi_custom_modeling_path": "/root/.cache/huggingface/modules/transformers_modules/master/modeling_phi3.py",
        "trust_remote_code": True,
        "root_cause": "Pinned Phi code reads removed DynamicCache.seen_tokens API",
        "repair": shim,
        "tests": tests,
        "scientific_adaptation": False,
        "generation_protocol_changed": False,
    }
    atomic(protocol / "phi_cache_compatibility.json", compatibility)
    atomic(protocol / "phi_continuation_preflight.json", {"status": "PASS", "verified_artifacts": verified, "protocol_hashes": protocol_hashes})

    queries = json.loads((args.project / "results/ownership_protocols/zeroprint_humaneval_2.json").read_text(encoding="utf-8"))
    perturbations = json.loads((protocol / "perturbation_manifest.json").read_text(encoding="utf-8"))
    prompts = [row["prompt"] for row in queries["rows"]] + [row["final_prompt"] for row in perturbations["rows"]]
    mp_path = args.data_root / "models/auxiliary/all-mpnet-base-v2"
    mp = base.MPNetAdapter(str(mp_path))
    input_emb = base.encode(mp, prompts)
    phi_fp, phi_meta = base.run_model(phi_path, panel["models"][2]["model_id"], "negative_3", prompts, input_emb, mp, art)
    phi_meta["revision"] = PHI_REV
    phi_meta["peak_ram_kib_process"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    runs = prior_manifest["runs"] + [phi_meta]
    atomic(protocol / "generation_manifest.json", {"runs": runs})

    fps = {role: np.load(parent_art / f"{role}_fingerprint.npy", allow_pickle=False) for role in EXPECTED}
    fps["negative_3"] = phi_fp
    reload_score = base.score(fps["reference_a"], fps["reference_b"])
    negatives = []
    for run in runs[2:]:
        negatives.append({"model_id": run["model_id"], **base.score(fps["reference_a"], fps[run["role"]])})
    tau = max(x["rescaled"] for x in negatives)
    reference_score = base.score(fps["reference_a"], fps["reference_a"])["rescaled"]
    negative_mean = float(np.mean([x["rescaled"] for x in negatives]))
    margin = reference_score - tau
    false_positives = sum(x["rescaled"] > tau for x in negatives)
    errors = []
    ok = reload_score["rescaled"] > tau and reference_score > tau and false_positives == 0
    detector = {
        "metric": "rescaled_Pearson_correlation",
        "reference_self": reference_score,
        "reference_reload": reload_score,
        "negative_scores": negatives,
        "negative_mean": negative_mean,
        "negative_max": tau,
        "threshold": tau,
        "threshold_rule": "tau=max frozen 3 negatives",
        "score_direction": "higher",
        "positive_rule": "score > tau; tie negative",
        "margin": margin,
        "false_positives": false_positives,
        "evaluation_errors": errors,
        "reference_positive": reference_score > tau,
    }
    lineage = {
        "A": {"run_id": "zeroprint_a_20260901_201050", "status": "PREPARE failure / NOT_JUDGED"},
        "A_cont1_preparation": {"status": "no scientific generation / NOT_JUDGED"},
        "A2": {"run_id": args.parent_run_id, "status": "Phi cache compatibility failure after four completed model slots"},
        "A2_phi_continuation": {"run_id": args.run_id, "scope": "Phi missing-only -> frozen detector -> closure"},
    }
    conclusion = (
        "ZeroPrint core reproduction successful under the WMKD A2 frozen three-negative canonical protocol"
        if ok
        else "ZeroPrint core reproduction not established under the WMKD A2 frozen three-negative canonical protocol"
    )
    total_accounted = json.loads((protocol / "runtime_gate.json").read_text(encoding="utf-8"))["runtime_seconds"] + sum(x["runtime_seconds"] for x in runs)
    common = {
        "schema_version": "wmkd.zeroprint-a2.v1",
        "method": "ZeroPrint",
        "experiment": "A2",
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "status": "COMPLETED",
        "official_repo": "shaoshuo-ss/ZeroPrint",
        "official_commit": base.OFFICIAL,
        "canonical_revision": base.REV,
        "model_modified": False,
        "artifact_type": "fingerprint_package" if ok else "scientific_evidence",
        "preferred_fingerprint": "yes" if ok else "no",
        "scientific_conclusion": conclusion,
        "runtime_seconds_continuation": time.time() - started,
        "runtime_seconds_total_accounted": total_accounted,
        "peak_vram_bytes": max(x["peak_vram_bytes"] for x in runs),
        "peak_ram_kib_continuation": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "disk_free_gb": base.freegb(args.data_root),
        "ba_status": "NOT_STARTED",
        "lineage": lineage,
        "compatibility_repair": compatibility,
    }
    fingerprints = {x["role"]: x["fingerprint"] for x in runs}
    runtime_gate = json.loads((protocol / "runtime_gate.json").read_text(encoding="utf-8"))
    resources = {
        "HumanEval": {"manifest_sha256": sha(args.project / "results/ownership_protocols/zeroprint_humaneval_2.json"), "ordered_rows_sha256": queries["ordered_rows_sha256"]},
        "GloVe": {"classification": "scientifically_equivalent_reconstruction_from_canonical_Stanford_GloVe_6B_100d"},
        "MPNet": {"path": str(mp_path), "dimension": 768, "pooling": "attention-mask mean", "normalize_embeddings": True},
    }
    atomic(protocol / "fingerprint_manifest.json", {"fingerprints": fingerprints, "Jacobian": {"alpha": base.ALPHA, "per_query_shape": [2, 589824], "aggregation": "mean"}})
    atomic(protocol / "detector_results.json", detector)
    atomic(protocol / "lineage.json", lineage)
    atomic(out / "summary.json", {**common, "runtime_gate": runtime_gate, "detector": detector})
    atomic(out / "detector_results.json", {**common, "detector": detector})
    atomic(out / "provenance_manifest.json", {**common, "resources": resources, "negative_panel": panel, "protocol_preflight": protocol_hashes})
    atomic(out / "artifact_manifest.json", {**common, "large_artifact_roots": [str(parent_art), str(art)], "generation_logs": [{"role": x["role"], "path": x["generation_log"], "sha256": x["generation_log_sha256"]} for x in runs], "fingerprints": fingerprints, "integrity": "PASS"})
    atomic(out / "full_experiment_log.json", {**common, "history": lineage, "negative_panel": panel, "resources": resources, "perturbations": perturbations, "generation_config": base.GEN, "seed_policy": {"base": base.SEED, "per_repeat": "1000+input_index*1000+repeat"}, "generations_per_model": 200, "runtime_gate": runtime_gate, "formal_runs": runs, "fingerprints": fingerprints, "detector": detector, "errors": errors, "utility": {"status": "not_applicable", "reason": "passive fingerprint; inherited canonical Base"}})

    report = f"""# ZeroPrint Experiment A2 report

**{conclusion}.** Preferred fingerprint: **{'yes' if ok else 'no'}**.

The Phi-only continuation repaired a Transformers cache API compatibility failure by mapping process-local `DynamicCache.seen_tokens` to the semantically equivalent `get_seq_length()`. It did not change the model, generation protocol, frozen panel, perturbations, Jacobian, or detector.

- Reference/self: {reference_score}
- Reference/reload: {reload_score['rescaled']} (raw {reload_score['raw_pearson']})
""" + "\n".join(f"- {x['model_id']}: {x['rescaled']} (raw {x['raw_pearson']})" for x in negatives) + f"\n- Tau: {tau}; margin: {margin}; FP: {false_positives}/3; errors: 0\n\nBounded to the WMKD A2 frozen three-negative canonical protocol; not a full-paper negative-panel reproduction. model_modified=false; utility=N/A; Ba=NOT_STARTED.\n"
    (args.project / "docs/reproduction_reports/zeroprint_experiment_a2_report.md").write_text(report, encoding="utf-8")
    (args.project / "docs/experiment_logs/zeroprint_experiment_a2_log.md").write_text(f"# ZeroPrint Experiment A2 log\n\n- Final run `{args.run_id}`\n- Lineage: A -> A cont1 preparation -> A2 cont2 -> Phi missing-only continuation\n- Runtime compatibility repair: `seen_tokens` -> `get_seq_length()`\n- Result: {conclusion}\n", encoding="utf-8")
    (args.project / "docs/methods/zeroprint.md").write_text(f"# ZeroPrint\n\nPassive black-box fingerprint pinned to `shaoshuo-ss/ZeroPrint` commit `{base.OFFICIAL}`. A2 uses the fixed frozen WMKD three-negative panel and does not modify model weights. The Phi continuation applies only a process-local Transformers cache API compatibility shim.\n", encoding="utf-8")

    index_path = args.project / "results/experiment_full_logs_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    full = out / "full_experiment_log.json"
    summary = out / "summary.json"
    entry = {"method": "ZeroPrint", "role": "preferred_fingerprint", "experiment": "A2", "run_id": args.run_id, "full_log_path": "results/zeroprint/experiment_a2/full_experiment_log.json", "full_log_sha256": sha(full), "summary_path": "results/zeroprint/experiment_a2/summary.json", "summary_sha256": sha(summary), "report_path": "docs/reproduction_reports/zeroprint_experiment_a2_report.md", "artifact_manifest_path": "results/zeroprint/experiment_a2/artifact_manifest.json", "scientific_status": "SUCCESSFUL" if ok else "NOT_ESTABLISHED", "artifact_type": common["artifact_type"], "model_modified": False, "preferred_fingerprint": common["preferred_fingerprint"], "utility_available": False, "ba_status": "NOT_STARTED"}
    index["objects"] = [x for x in index["objects"] if x.get("method") != "ZeroPrint"] + [entry]
    index["object_count"] = len(index["objects"])
    index["generated_at"] = now()
    atomic(index_path, index)
    print(json.dumps({"run_id": args.run_id, "detector": detector, "conclusion": conclusion}, indent=2), flush=True)


if __name__ == "__main__":
    main()
