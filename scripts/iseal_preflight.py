"""Minimal fail-closed static/runtime preflight for iSeal Experiment A."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--source-archive", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    model = Path(config["model"]["path"])
    source = Path(args.source_root)
    archive = Path(args.source_archive)
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None
    checks = {
        "fixed_model_revision": config["model"]["revision"] == "0cb88a4f764b7a12671c53f0838cd831a0843b95",
        "canonical_model_exists": model.is_dir(),
        "canonical_model_file_count": model.is_dir() and len([p for p in model.iterdir() if p.is_file()]) == config["model"]["expected_files"],
        "canonical_model_bytes": model.is_dir() and sum(p.stat().st_size for p in model.iterdir() if p.is_file()) == config["model"]["expected_bytes"],
        "pinned_source_archive": archive_hash == config["official_source"]["archive_sha256"],
        "pinned_source_archive_bytes": archive.is_file() and archive.stat().st_size == config["official_source"]["archive_bytes"],
        "official_relevant_files": all((source / item).is_file() for item in config["official_source"]["relevant_files"]),
        "runtime_dependencies": all(importlib.util.find_spec(name) is not None for name in ("torch", "transformers", "datasets", "sacrebleu", "yaml")),
        "formal_config": config["dataset"]["registered_count"] == 10 and config["training"]["epochs"] == 15 and config["training"]["learning_rate"] == 1e-3 and config["training"]["adapter_inner_dim"] == 16,
        "trainability_gate_required": config["trainability_audit"]["fail_if_adapter_not_updated"] is True,
    }
    result = {"checks": checks, "blockers": [name for name, passed in checks.items() if not passed]}
    result["ready_for_trainability_audit"] = not result["blockers"]
    path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ready_for_trainability_audit"] else 2)


if __name__ == "__main__":
    main()
