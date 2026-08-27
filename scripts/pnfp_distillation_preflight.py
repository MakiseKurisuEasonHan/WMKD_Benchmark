#!/usr/bin/env python3
"""CPU-only preflight and dry-run plan for PN-FP Ba/Bb."""

import argparse
import json
import os
from pathlib import Path


DATA_ROOT = Path("/root/autodl-tmp/WMKD_Benchmark_data")


def load_config(path: Path) -> dict:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for distillation configs") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("config root must be a mapping")
    return data


def validate_config(config: dict) -> None:
    training = config["training"]
    if training["lora"] or not training["full_parameter"]:
        raise ValueError("formal Ba/Bb require full-parameter training with LoRA OFF")
    if training["batch_size"] != 8 or training["batch_fallback"] != [8, 4, 2]:
        raise ValueError("batch policy must be 8 -> 4 -> 2 only after genuine OOM")
    if config["dataset"]["final_samples"] != 20000:
        raise ValueError("formal paired dataset must contain exactly 20,000 samples")
    revision = str(config["student"]["revision"])
    if len(revision) != 40 or revision in {"main", "master"}:
        raise ValueError("student revision must be an exact 40-character commit")
    for key, value in config["paths"].items():
        path = Path(str(value))
        if path.is_absolute() and path != DATA_ROOT and DATA_ROOT not in path.parents:
            raise ValueError(f"large-artifact path outside data disk: {key}={path}")
    forbidden = (Path("/root/.cache"), Path.home() / ".cache")
    for env_name in ("HF_HOME", "HF_HUB_CACHE", "HF_DATASETS_CACHE", "TRANSFORMERS_CACHE"):
        value = os.environ.get(env_name)
        if value and any(Path(value) == item or item in Path(value).parents for item in forbidden):
            raise ValueError(f"{env_name} points to system-disk cache: {value}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_config(Path(args.config))
    validate_config(config)
    print(json.dumps({"status": "ready", "experiment": config["experiment"], "dry_run": args.dry_run}))


if __name__ == "__main__":
    main()
