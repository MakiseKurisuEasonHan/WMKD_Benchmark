#!/usr/bin/env python3
"""Archive the canonical Passive-5 Shared Bb3 Student with Ba's audited machinery."""
import json
from pathlib import Path

import modelscope_passive5_ba_student_archive as archive


archive.ARCHIVE_SLUG = "passive5_shared_bb3"
archive.EXPERIMENT_LABEL = "Bb3"
archive.OBJECT_SLUG = "canonical_passive5_shared_bb3_final_student"
archive.SCHEMA_VERSION = "wmkd.modelscope-passive5-shared-bb3-student.v1"
archive.EVALUATION_RUN_ID = "passive5_shared_bb3_20260903_164929"
archive.REPO_NAME = "Llama-3.2-WMKD-Passive5-Shared-Bb3-Student"
archive.REPO_ID = f"{archive.NAMESPACE}/{archive.REPO_NAME}"
archive.SOURCE = Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/passive5_shared_bb3/passive5_shared_bb3_20260903_164929/student/final_model")
archive.SOURCE_MANIFEST = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/student_manifest.json")
archive.TRAINING_SUMMARY = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/training_summary.json")
archive.FULL_LOG = Path("/root/autodl-tmp/WMKD_Benchmark/results/passive5_shared_bb3/full_experiment_log.json")
archive.EXPECTED_SOURCE_FILES = {
    "config.json", "generation_config.json", "model-00001-of-00002.safetensors",
    "model-00002-of-00002.safetensors", "model.safetensors.index.json",
    "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "training_args.bin",
}


def bb3_source_gate() -> dict:
    source = archive.SOURCE
    entries = list(source.iterdir())
    if any(p.is_symlink() for p in entries) or any(p.is_dir() for p in entries):
        raise RuntimeError("SOURCE_LAYOUT_INVALID")
    names = {p.name for p in entries}
    if names != archive.EXPECTED_SOURCE_FILES or any(p.stat().st_size == 0 for p in entries):
        raise RuntimeError(f"SOURCE_FILE_SET_MISMATCH {sorted(names)}")
    manifest = json.loads(archive.SOURCE_MANIFEST.read_text(encoding="utf-8"))
    summary = json.loads(archive.TRAINING_SUMMARY.read_text(encoding="utf-8"))
    full = json.loads(archive.FULL_LOG.read_text(encoding="utf-8"))
    hashes = {name: archive.sha256(source / name) for name in sorted(names)}
    if manifest.get("status") != "PASS" or manifest.get("artifact") != str(source) or manifest.get("files_sha256") != hashes:
        raise RuntimeError("SOURCE_MANIFEST_GATE_FAILED")
    cfg = summary.get("configuration", {})
    required = {"epochs":3, "learning_rate":1e-5, "precision":"bf16", "full_parameter":True,
                "lora":False, "effective_batch_size":8, "expected_steps":7500}
    if any(cfg.get(k) != v for k, v in required.items()) or summary.get("optimizer_steps") != 7500:
        raise RuntimeError("TRAINING_CONFIGURATION_GATE_FAILED")
    reload_info = full.get("reload_validation", {})
    if reload_info.get("status") != "PASS" or reload_info.get("fresh_process_reload") is not True:
        raise RuntimeError("FRESH_RELOAD_EVIDENCE_GATE_FAILED")
    index = json.loads((source / "model.safetensors.index.json").read_text(encoding="utf-8"))
    shards = set(index.get("weight_map", {}).values())
    if shards != {"model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"}:
        raise RuntimeError("SHARD_INDEX_GATE_FAILED")
    config = json.loads((source / "config.json").read_text(encoding="utf-8"))
    if config.get("architectures") != ["LlamaForCausalLM"] or config.get("torch_dtype") != "bfloat16":
        raise RuntimeError("MODEL_IDENTITY_GATE_FAILED")
    manifest_for_archive = {**manifest, "run_id":archive.EVALUATION_RUN_ID}
    return {"hashes":hashes, "sizes":{n:(source / n).stat().st_size for n in sorted(names)},
            "manifest":manifest_for_archive, "summary":summary, "reload":reload_info,
            "model":{"architecture":"LlamaForCausalLM", "parameters":reload_info["finite_weight_check"]["parameter_count"],
                     "weight_bytes":index["metadata"]["total_size"], "dtype":"bfloat16"}}


archive.source_gate = bb3_source_gate


if __name__ == "__main__":
    archive.main()
