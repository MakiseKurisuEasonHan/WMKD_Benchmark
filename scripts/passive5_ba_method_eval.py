#!/usr/bin/env python3
"""Frozen-protocol method evaluators for Passive-5 Shared Ba/Bb Students."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_npy(path: Path, value: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.save(handle, value)
    os.replace(temporary, path)


def experiment_slug(args: argparse.Namespace) -> str:
    return args.experiment.casefold()


def student_label(args: argparse.Namespace) -> str:
    return f"WMKD/Passive5-Shared-{args.experiment}-Student"


def centered_linear_cka(left: np.ndarray, right: np.ndarray) -> float:
    left = left.astype(np.float64) - left.astype(np.float64).mean(axis=0, keepdims=True)
    right = right.astype(np.float64) - right.astype(np.float64).mean(axis=0, keepdims=True)
    numerator = np.linalg.norm(left.T @ right, ord="fro") ** 2
    denominator = np.linalg.norm(left.T @ left, ord="fro") * np.linalg.norm(right.T @ right, ord="fro")
    return float(numerator / denominator)


def reef(args: argparse.Namespace) -> None:
    started = time.time()
    method_dir = args.output / "reef"
    probe_path = args.project / "results/ownership_protocols/reef_truthfulqa_200.json"
    expected_probe_sha = "8f63355817f726faea792edcc393ef9c6d32e07449bb66bbdefeb201e636599f"
    if sha256(probe_path) != expected_probe_sha:
        raise RuntimeError("REEF_FROZEN_PROBE_SHA_MISMATCH")
    probes = json.loads(probe_path.read_text(encoding="utf-8"))
    if probes["ordered_rows_sha256"] != "ea3f17daffe6b9e82ffcb5f43b1efe0e88483708c6261f532ed007555ac6c79f":
        raise RuntimeError("REEF_ORDERED_ROWS_SHA_MISMATCH")
    prompts = [row["text"] for row in probes["rows"]]
    if len(prompts) != 200:
        raise RuntimeError("REEF_PROBE_COUNT_MISMATCH")
    reference_path = Path("/root/autodl-tmp/WMKD_Benchmark_data/artifacts/reef/experiment_a/protocol_compliance/reef_a_protocol_cont1_20260901_202500/reference_reload_a.npy")
    expected_reference_sha = "99ba4449d578a39a6709fc37e4e0ae709eb3b3f20d0e0a76633411e69705d525"
    if sha256(reference_path) != expected_reference_sha:
        raise RuntimeError("REEF_REFERENCE_SHA_MISMATCH")
    reference = np.load(reference_path)
    if reference.shape != (200, 3072):
        raise RuntimeError("REEF_REFERENCE_SHAPE_MISMATCH")

    torch.cuda.reset_peak_memory_stats()
    tokenizer = AutoTokenizer.from_pretrained(args.student, local_files_only=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.student, local_files_only=True, trust_remote_code=True,
        torch_dtype=torch.float16, device_map="cuda:0",
    ).eval()
    blocks = model.model.layers
    if len(blocks) != 28:
        raise RuntimeError("REEF_STUDENT_LAYER_COUNT_MISMATCH")
    captured: list[torch.Tensor] = []

    def hook(_module, _inputs, output):
        value = output[0] if isinstance(output, tuple) else output
        captured.append(value[:, -1, :].detach().float().cpu())

    handle = blocks[27].register_forward_hook(hook)
    rows = []
    try:
        with torch.inference_mode():
            for prompt in prompts:
                encoded = tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to("cuda:0")
                model(**encoded, use_cache=False)
                if len(captured) != 1:
                    raise RuntimeError("REEF_HOOK_CARDINALITY_MISMATCH")
                rows.append(captured.pop().numpy()[0])
    finally:
        handle.remove()
    student_representation = np.asarray(rows, dtype=np.float32)
    if student_representation.shape != (200, 3072) or not np.isfinite(student_representation).all():
        raise RuntimeError("REEF_STUDENT_REPRESENTATION_INVALID")
    representation_path = method_dir / "student_representation.npy"
    atomic_npy(representation_path, student_representation)
    score = centered_linear_cka(reference, student_representation)
    threshold = 0.4546738923165847
    result = {
        "schema_version": f"wmkd.passive5-shared-{experiment_slug(args)}-reef.v1",
        "method": "REEF",
        "experiment": args.experiment,
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "status": "COMPLETED",
        "student_fresh_reload": True,
        "student_path": str(args.student),
        "frozen_protocol": {
            "probe_manifest_path": str(probe_path),
            "probe_manifest_sha256": expected_probe_sha,
            "ordered_rows_sha256": probes["ordered_rows_sha256"],
            "sample_count": 200,
            "layer": 27,
            "semantics": "exact raw decoder-block forward-hook output[0] at last token",
            "metric": "centered_linear_CKA",
            "threshold": threshold,
            "positive_rule": "score > threshold; tie is negative",
            "calibration_reused": True,
        },
        "reference_representation": {
            "path": str(reference_path),
            "sha256": expected_reference_sha,
            "shape": list(reference.shape),
        },
        "student_representation": {
            "path": str(representation_path),
            "sha256": sha256(representation_path),
            "shape": list(student_representation.shape),
            "dtype": str(student_representation.dtype),
        },
        "score": score,
        "threshold": threshold,
        "positive": score > threshold,
        "peak_vram_bytes": int(torch.cuda.max_memory_allocated()),
        "runtime_seconds": time.time() - started,
        "completed_at": now(),
        "errors": [],
    }
    atomic_json(method_dir / "detector_result.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


def huref(args: argparse.Namespace) -> None:
    started = time.time()
    method_dir = args.output / "huref"
    manifest_path = args.project / "results/huref/experiment_a2/protocol/token_manifests/meta-llama--Llama-3.2-3B-Instruct.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest_content_sha = "cbc7a9978f349c88afad65f6bf854234a7d4dff6cca5f6a47b88d84498d95e79"
    if manifest.get("manifest_content_sha256") != expected_manifest_content_sha:
        raise RuntimeError("HUREF_FROZEN_TOKEN_MANIFEST_SHA_MISMATCH")
    if manifest.get("K") != 4096 or manifest.get("invalid_count") != 0 or len(manifest.get("rows", [])) != 4096:
        raise RuntimeError("HUREF_FROZEN_TOKEN_MANIFEST_INVALID")
    tokenizer_files = {item["name"]: item["sha256"] for item in manifest["tokenizer_files"]}
    observed_tokenizer_files = {}
    tokenizer_file_identity = {}
    for name, expected in tokenizer_files.items():
        path = args.student / name
        observed = sha256(path)
        observed_tokenizer_files[name] = observed
        tokenizer_file_identity[name] = observed == expected

    sys.path.insert(0, str(args.project / "scripts"))
    import huref_experiment_a2 as protocol
    corpus_manifest_path = args.project / "results/huref/experiment_a2/protocol/corpus_manifest.json"
    corpus_manifest = json.loads(corpus_manifest_path.read_text(encoding="utf-8"))
    corpus_path = Path(corpus_manifest["source"])
    if sha256(corpus_path) != corpus_manifest["source_sha256"]:
        raise RuntimeError("HUREF_CORPUS_SOURCE_SHA_MISMATCH")
    corpus_rows = protocol.iter_corpus(corpus_path, 10000)
    rebuilt_manifest = protocol.build_token_manifest(
        student_label(args), args.parent_run_id, args.student,
        corpus_rows, manifest["corpus_sha256"],
    )
    expected_ids = [int(row["token_id"]) for row in manifest["rows"]]
    rebuilt_ids = [int(row["token_id"]) for row in rebuilt_manifest["rows"]]
    if rebuilt_ids != expected_ids:
        raise RuntimeError("HUREF_STUDENT_TOPK_TOKEN_IDS_OR_ORDER_DIFFER")
    atomic_json(method_dir / "student_token_manifest.json", rebuilt_manifest)
    ids = rebuilt_ids
    reference_path = args.project / "results/huref/experiment_a2/protocol/reference_a--meta-llama--Llama-3.2-3B-Instruct.npy"
    expected_reference_sha = "ed43610236f89d8f0e367c8f9073b409327e7045d2184e12fdd509ddd2a9e04c"
    if sha256(reference_path) != expected_reference_sha:
        raise RuntimeError("HUREF_REFERENCE_FEATURE_SHA_MISMATCH")
    reference = np.load(reference_path, allow_pickle=False)
    if reference.shape != (512,) or not np.isfinite(reference).all():
        raise RuntimeError("HUREF_REFERENCE_FEATURE_INVALID")

    student_feature_path = method_dir / "student_feature.npy"
    student_feature, extraction = protocol.extract(
        args.student, ids, student_feature_path, student_label(args),
        rebuilt_manifest["manifest_content_sha256"],
    )
    score = protocol.ics(reference, student_feature)
    threshold = 4.119894027709961
    result = {
        "schema_version": f"wmkd.passive5-shared-{experiment_slug(args)}-huref.v1",
        "method": "HuRef",
        "experiment": args.experiment,
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "status": "COMPLETED",
        "student_fresh_reload": True,
        "student_path": str(args.student),
        "frozen_protocol": {
            "experiment_a_source": "A2",
            "token_manifest_path": str(manifest_path),
            "reference_token_manifest_content_sha256": expected_manifest_content_sha,
            "student_token_manifest_content_sha256": rebuilt_manifest["manifest_content_sha256"],
            "student_token_manifest_path": str(method_dir / "student_token_manifest.json"),
            "student_topk_ids_and_order_identical_to_reference": True,
            "K": 4096,
            "student_tokenizer_files_sha256": observed_tokenizer_files,
            "student_tokenizer_file_byte_identity": tokenizer_file_identity,
            "layers": [26, 27],
            "term_order": protocol.ORDER,
            "pooling": "official mean pooling to globally standardized 512-d feature",
            "metric": "official ICS = 100*cosine_similarity of globally standardized flattened 512-d features",
            "threshold": threshold,
            "positive_rule": "score > threshold; tie is negative",
            "calibration_reused": True,
        },
        "reference_feature": {
            "path": str(reference_path),
            "sha256": expected_reference_sha,
            "shape": list(reference.shape),
        },
        "student_extraction": extraction,
        "score": score,
        "threshold": threshold,
        "positive": score > threshold,
        "runtime_seconds": time.time() - started,
        "completed_at": now(),
        "errors": [],
    }
    atomic_json(method_dir / "detector_result.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


def awm(args: argparse.Namespace) -> None:
    started = time.time()
    method_dir = args.output / "awm"
    sys.path.insert(0, str(args.project / "scripts"))
    import awm_protocol_cont1 as protocol
    frozen = json.loads((args.project / "results/awm/experiment_a/detector_results.json").read_text(encoding="utf-8"))
    detector = frozen["detector"]
    threshold = float(detector["threshold"])
    if threshold != 0.0017953364917795106:
        raise RuntimeError("AWM_FROZEN_THRESHOLD_MISMATCH")
    base = Path("/root/autodl-tmp/WMKD_Benchmark_data/models/base/Llama-3.2-3B-Instruct")
    reference = protocol.extract(base, "meta-llama/Llama-3.2-3B-Instruct", protocol.REV)
    student = protocol.extract(args.student, student_label(args), args.parent_run_id)
    official_metric = protocol.official()
    score, dimension_alignment, layer_alignment = protocol.compare(
        reference, student, method_dir / "progress.json", official_metric,
    )
    result = {
        "schema_version": f"wmkd.passive5-shared-{experiment_slug(args)}-awm.v1",
        "method": "AWM",
        "experiment": args.experiment,
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "status": "COMPLETED",
        "student_fresh_reload": True,
        "student_path": str(args.student),
        "frozen_protocol": {
            "official_repo": "LUMIA-Group/AWM",
            "official_commit": protocol.OFFICIAL,
            "metric": "official_mean_Wq_Wk_unbiased_linear_CKA",
            "dimension_alignment": "overlapping-vocabulary Hungarian LAP with sign correction",
            "layer_alignment": "identity for equal layer counts; official LAP otherwise",
            "threshold": threshold,
            "positive_rule": "score > threshold; tie is negative",
            "calibration_reused": True,
        },
        "reference": protocol.strip(reference),
        "student": protocol.strip(student),
        "dimension_alignment": dimension_alignment,
        "layer_alignment": layer_alignment,
        "score": score,
        "threshold": threshold,
        "positive": score > threshold,
        "runtime_seconds": time.time() - started,
        "completed_at": now(),
        "errors": [],
    }
    atomic_json(method_dir / "detector_result.json", result)
    print(json.dumps({"method": "AWM", "score": score, "threshold": threshold,
                      "positive": score > threshold, "runtime_seconds": result["runtime_seconds"]}), flush=True)


def zeroprint(args: argparse.Namespace) -> None:
    started = time.time()
    method_dir = args.output / "zeroprint"
    method_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.project / "scripts"))
    import zeroprint_experiment_a2 as protocol
    query_path = args.project / "results/ownership_protocols/zeroprint_humaneval_2.json"
    if sha256(query_path) != "72fc6cf6c25e2d955178fa90eb765afbc790bd5d576515447c86ced95149019c":
        raise RuntimeError("ZEROPRINT_HUMANEVAL_MANIFEST_SHA_MISMATCH")
    queries = json.loads(query_path.read_text(encoding="utf-8"))
    perturbation_path = args.project / "results/zeroprint/experiment_a2/protocol/perturbation_manifest.json"
    perturbations = json.loads(perturbation_path.read_text(encoding="utf-8"))
    if perturbations.get("manifest_content_sha256") != "79c189d042e0dd05dd97effc6a377380b823046d35906b395473a14ea78dec36":
        raise RuntimeError("ZEROPRINT_PERTURBATION_MANIFEST_SHA_MISMATCH")
    prompts = [row["prompt"] for row in queries["rows"]] + [row["final_prompt"] for row in perturbations["rows"]]
    if len(prompts) != 10:
        raise RuntimeError("ZEROPRINT_PROMPT_COUNT_MISMATCH")
    mpnet_path = Path("/root/autodl-tmp/WMKD_Benchmark_data/models/auxiliary/all-mpnet-base-v2")
    if sha256(mpnet_path / "config.json") != "d46a3e04ded82bba22528424480697d394eeda6a27484e08c5bb2bdf5906cfa0":
        raise RuntimeError("ZEROPRINT_MPNET_CONFIG_SHA_MISMATCH")
    reference_path = Path("/root/autodl-tmp/WMKD_Benchmark_data/artifacts/zeroprint/experiment_a2/zeroprint_a2_20260902_060000_cont2/reference_a_fingerprint.npy")
    expected_reference_sha = "580ece1cf0c2c6d498a8e4abd212f19601752354467071735307f1d55aea6b11"
    if sha256(reference_path) != expected_reference_sha:
        raise RuntimeError("ZEROPRINT_REFERENCE_FINGERPRINT_SHA_MISMATCH")
    reference = np.load(reference_path, allow_pickle=False)
    if reference.shape != (589824,) or not np.isfinite(reference).all():
        raise RuntimeError("ZEROPRINT_REFERENCE_FINGERPRINT_INVALID")
    mpnet = protocol.MPNetAdapter(str(mpnet_path))
    input_embeddings = protocol.encode(mpnet, prompts)
    student_fingerprint, generation = protocol.run_model(
        args.student, student_label(args), "student",
        prompts, input_embeddings, mpnet, method_dir,
    )
    detector_score = protocol.score(reference, student_fingerprint)
    threshold = 0.6793505996465683
    result = {
        "schema_version": f"wmkd.passive5-shared-{experiment_slug(args)}-zeroprint.v1",
        "method": "ZeroPrint",
        "experiment": args.experiment,
        "run_id": args.run_id,
        "parent_run_id": args.parent_run_id,
        "status": "COMPLETED",
        "student_fresh_reload": True,
        "student_path": str(args.student),
        "frozen_protocol": {
            "official_repo": "shaoshuo-ss/ZeroPrint",
            "official_commit": protocol.OFFICIAL,
            "query_manifest_path": str(query_path),
            "query_manifest_sha256": sha256(query_path),
            "perturbation_manifest_path": str(perturbation_path),
            "perturbation_manifest_content_sha256": perturbations["manifest_content_sha256"],
            "generation_config": protocol.GEN,
            "seed_policy": "1000 + input_index*1000 + repeat",
            "generations": 200,
            "mpnet_path": str(mpnet_path),
            "ridge_alpha": protocol.ALPHA,
            "metric": "rescaled_Pearson_correlation",
            "threshold": threshold,
            "positive_rule": "score > threshold; tie is negative",
            "calibration_reused": True,
        },
        "reference_fingerprint": {
            "path": str(reference_path), "sha256": expected_reference_sha,
            "shape": list(reference.shape),
        },
        "student_generation": generation,
        "score": detector_score,
        "threshold": threshold,
        "positive": detector_score["rescaled"] > threshold,
        "runtime_seconds": time.time() - started,
        "completed_at": now(),
        "errors": [],
    }
    atomic_json(method_dir / "detector_result.json", result)
    print(json.dumps({"method": "ZeroPrint", "score": detector_score, "threshold": threshold,
                      "positive": result["positive"], "runtime_seconds": result["runtime_seconds"]}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parent-run-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--method", choices=("reef", "huref", "awm", "zeroprint"), required=True)
    parser.add_argument("--experiment", choices=("Ba", "Bb"), default="Ba")
    args = parser.parse_args()
    if args.method == "reef":
        reef(args)
    elif args.method == "huref":
        huref(args)
    elif args.method == "awm":
        awm(args)
    elif args.method == "zeroprint":
        zeroprint(args)


if __name__ == "__main__":
    main()
