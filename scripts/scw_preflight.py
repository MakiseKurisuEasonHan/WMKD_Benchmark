"""Fail-closed local/future-runtime preflight for SCW Experiment A."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scw_common import canonical_json_sha256, load_config, validate_config


def build_preflight(config_path: Path) -> dict:
    config = load_config(config_path)
    errors = validate_config(config)
    return {
        "project": "WMKD_Benchmark",
        "method": "SCW",
        "experiment": "A",
        "mode": "static_local",
        "status": "READY_FOR_FUTURE_AUTODL_PREFLIGHT" if not errors else "BLOCKED",
        "config_path": str(config_path),
        "config_sha256": canonical_json_sha256(config),
        "checks": {
            "official_commit_pinned": not any("official source" in e for e in errors),
            "canonical_model_revision_pinned": not any("canonical model" in e for e in errors),
            "scientific_config_fixed": not any("mismatch" in e for e in errors),
            "full_parameter_intent": config["training"]["mode"] == "full_parameter" and config["training"]["lora"] is False,
            "runtime_trainable_count_required": config["training"]["runtime_dtype_assertion_required"],
            "formal_run_not_started": config["safety"]["formal_run_started"] is False,
            "ba_not_started": config["safety"]["ba_started"] is False,
        },
        "runtime_gates_pending": [
            "official source tree exact commit and license present",
            "canonical model 12-file SHA manifest and revision",
            "dataset revisions/stream identities and observed 0.6/0.2/0.2 proportions",
            "model parameter dtype and actual compute/autocast dtype",
            "optimizer class, effective batch, sequence length, active losses",
            "unique trainable parameters equal unique model parameters; no LoRA/freeze",
            "GPU idle and output namespace absent",
        ],
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/watermark/scw_experiment_a.yaml")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = build_preflight(Path(args.config))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if result["status"].startswith("READY") else 1)


if __name__ == "__main__":
    main()
