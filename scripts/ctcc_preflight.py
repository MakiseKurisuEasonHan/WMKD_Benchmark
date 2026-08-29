"""Fail-closed minimal preflight for CTCC Experiment A."""

import argparse
import json
from pathlib import Path
import shutil

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--serialization-audit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    serialization = json.loads(Path(args.serialization_audit).read_text(encoding="utf-8"))
    checks = {}
    model = Path(config["model"]["path"])
    checks["canonical_model_exists"] = model.is_dir()
    checks["canonical_model_file_count"] = len([p for p in model.iterdir() if p.is_file()]) == config["model"]["expected_files"] if model.is_dir() else False
    checks["canonical_model_bytes"] = sum(p.stat().st_size for p in model.iterdir() if p.is_file()) == config["model"]["expected_bytes"] if model.is_dir() else False
    checks["official_source_files_frozen"] = all(Path(item["frozen_path"]).is_file() for item in manifest["files"].values())
    checks["serialization_roles_and_content"] = serialization.get("passed") is True
    checks["training_count_matches_fixed_protocol"] = manifest["training_counts"] == config["dataset"]["expected_counts"]
    checks["test_count_matches_fixed_protocol"] = {k: v["total"] for k, v in manifest["test_positional_categories"].items()} == config["dataset"]["expected_test_counts"]
    checks["fixed_model_revision"] = config["model"]["revision"] == "0cb88a4f764b7a12671c53f0838cd831a0843b95"
    training = config["training"]
    checks["fixed_training_config"] = (
        training["epochs"] == 12 and training["learning_rate"] == 1e-4
        and training["cutoff_len"] == 2048 and training["packing"] is False
        and training["lora_rank"] == 8 and training["lora_alpha"] == 16
        and training["lora_dropout"] == 0 and training["lora_target"] == "all"
        and training["per_device_train_batch_size"] == 8
        and training["gradient_accumulation_steps"] == 2
        and config["seed"] == 48 and training["precision"] == "bf16"
    )
    checks["llamafactory_cli_available"] = shutil.which("llamafactory-cli") is not None
    blockers = [name for name, passed in checks.items() if not passed]
    result = {"checks": checks, "blockers": blockers, "ready_to_launch": not blockers}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not blockers else 2)


if __name__ == "__main__":
    main()
