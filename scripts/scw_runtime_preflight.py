"""Future AutoDL runtime-effective SCW gate. Never invoked by local static tests."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scw_common import canonical_json_sha256, load_config, validate_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--official-source", required=True)
    parser.add_argument("--dataset-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    errors = validate_config(config)
    source = Path(args.official_source).resolve()
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != config["official_source"]["commit"]:
        errors.append("official source commit mismatch")
    if not (source / "LICENSE_CODE").is_file():
        errors.append("official LICENSE_CODE missing")
    gpu = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    )
    if gpu.stdout.strip():
        errors.append("GPU is not idle")
    manifest = json.loads(Path(args.dataset_manifest).read_text(encoding="utf-8"))
    expected_names = config["datasets"]["names"] + ["FrenchEvaluation"]
    if manifest.get("dataset_names") != expected_names:
        errors.append("dataset manifest names/order mismatch")
    if not all(row.get("revision") and row.get("revision") != "RESOLVE_AND_PIN_BEFORE_FORMAL_RUN" for row in manifest.get("datasets", [])):
        errors.append("every dataset requires a pinned revision/immutable identity")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_path = Path(config["model"]["future_path"]).resolve()
    if not model_path.is_dir():
        errors.append("canonical model path missing")
        model = None
    else:
        AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True, device_map="cuda", torch_dtype="auto")
    dtype_counts: dict[str, int] = {}
    unique_total = unique_trainable = 0
    seen: set[int] = set()
    if model is not None:
        for parameter in model.parameters():
            identity = id(parameter)
            if identity in seen:
                continue
            seen.add(identity)
            count = parameter.numel()
            unique_total += count
            if parameter.requires_grad:
                unique_trainable += count
            dtype_counts[str(parameter.dtype)] = dtype_counts.get(str(parameter.dtype), 0) + count
        if unique_trainable != unique_total:
            errors.append("full-parameter gate failed: unique trainable count != unique total count")
    result = {
        "project": "WMKD_Benchmark", "method": "SCW", "experiment": "A",
        "status": "READY" if not errors else "BLOCKED",
        "config_sha256": canonical_json_sha256(config),
        "official_commit": commit,
        "model_path": str(model_path),
        "model_revision": config["model"]["revision"],
        "unique_total_parameters": unique_total,
        "unique_trainable_parameters": unique_trainable,
        "model_parameter_dtype_counts": dtype_counts,
        "runtime_compute_dtype": "MUST_BE_RECORDED_BY_FIRST_REAL_FORWARD/TRAIN_STEP",
        "optimizer": config["training"]["optimizer"],
        "effective_batch": config["training"]["effective_batch_size"],
        "sequence_length": config["training"]["sequence_length"],
        "datasets": manifest,
        "expected_proportions": config["datasets"]["proportions"],
        "active_losses": config["datasets"]["loss_types"],
        "gpu_idle": not bool(gpu.stdout.strip()),
        "errors": errors,
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result["status"] == "READY" else 1)


if __name__ == "__main__":
    main()
