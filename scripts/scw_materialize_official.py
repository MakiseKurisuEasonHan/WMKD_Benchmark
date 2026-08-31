"""Future AutoDL entry point: freeze the pinned official SCW finite stream.

This script is prepared locally and must not be run until a separately
authorized AutoDL materialization stage.  It never modifies official source.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from scw_common import CANONICAL_MODEL, CANONICAL_REVISION, OFFICIAL_COMMIT, load_config
from scw_materialized_stream import build_manifest, materialize_records, training_length_contract, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--official-runtime-config", required=True)
    parser.add_argument("--official-source", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--creation-code-version", required=True)
    parser.add_argument("--tiny-validation-records", type=int)
    args = parser.parse_args()
    config = load_config(args.config)
    if os.environ.get("PYTHONHASHSEED") != str(config["training"]["pythonhashseed"]):
        raise RuntimeError("PYTHONHASHSEED must be fixed before interpreter startup")
    source = Path(args.official_source).resolve()
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != OFFICIAL_COMMIT:
        raise RuntimeError("official source commit mismatch")
    if subprocess.run(["git", "-C", str(source), "diff", "--quiet", "HEAD", "--"]).returncode or subprocess.run(["git", "-C", str(source), "diff", "--cached", "--quiet"]).returncode:
        raise RuntimeError("official tracked source must remain clean")
    sys.path.insert(0, str(source / "src"))
    # Pin revisions before importing the official dataset module, whose
    # ``from datasets import load_dataset`` binding occurs at import time.
    import datasets as hf_datasets
    revisions = {
        "OpenLLM-France/Lucie-Training-Dataset": "8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1",
        "vicgalle/alpaca-gpt4": "f7e3ded725cb81e8e564e32feb12860f376f2b51",
        "Skylion007/openwebtext": "79d93d786212f7344586290adb811d4ae6a1762c",
    }
    original_load_dataset = hf_datasets.load_dataset

    def pinned_load_dataset(path, *load_args, **kwargs):
        if path in revisions:
            requested = kwargs.setdefault("revision", revisions[path])
            if requested != revisions[path]:
                raise RuntimeError(f"dataset revision mismatch for {path}: {requested}")
        return original_load_dataset(path, *load_args, **kwargs)

    hf_datasets.load_dataset = pinned_load_dataset
    from robust_fp.config import MainConfiguration
    from robust_fp.finetuning.finetune import load_datasets_from_config
    from transformers import AutoTokenizer

    runtime = MainConfiguration.parse_yaml(args.official_runtime_config)
    ft = runtime.finetuning_config
    if ft is None or str(runtime.base_model) != config["model"]["future_path"]:
        raise RuntimeError("official runtime config/model mismatch")
    tokenizer = AutoTokenizer.from_pretrained(ft.base_model, padding_side="left")
    from robust_fp.finetuning.data_utils import add_chat_template
    if tokenizer.chat_template is None:
        tokenizer = add_chat_template(tokenizer)
    official_stream, _type_processor = load_datasets_from_config(ft, tokenizer)
    if args.tiny_validation_records is not None:
        if not 1 <= args.tiny_validation_records <= 32:
            raise RuntimeError("tiny validation must contain between 1 and 32 records")
        validation = materialize_records(official_stream, args.records, args.tiny_validation_records)
        rows = [json.loads(line) for line in Path(args.records).read_text(encoding="utf-8").splitlines()]
        expected_losses = {0: "watermark", 1: "anti-watermark-tv", 2: "anti-watermark-tv"}
        if any(row["loss_type"] != expected_losses[row["label_id"]] for row in rows):
            raise RuntimeError("tiny validation label/loss mapping mismatch")
        print(json.dumps({"status": "TINY_VALIDATION_PASS", **validation}, indent=2))
        return
    contract = training_length_contract(ft.training_args["max_steps"], ft.training_args["gradient_accumulation_steps"], ft.training_args["per_device_train_batch_size"])
    materialization = materialize_records(official_stream, args.records, contract["expected_consumed_examples"])
    seeds = {
        "LucieFr_shuffle": hash(ft.watermark_datasets[0]) % 2**sys.hash_info.width,
        "AlpacaGPT4_shuffle": hash(ft.regularization_datasets[0]) % 2**sys.hash_info.width,
        "OpenWebText_shuffle": hash(ft.regularization_datasets[1]) % 2**sys.hash_info.width,
        "interleave": hash(ft.short_str()) % 2**sys.hash_info.width,
    }
    provenance = {
        "official_repo_commit": OFFICIAL_COMMIT,
        "creation_code_version": args.creation_code_version,
        "model": {"id": CANONICAL_MODEL, "revision": CANONICAL_REVISION},
        "datasets": [{**row, "revision": revisions[row["path"]]} for row in config["datasets"]["sources"]],
        "pythonhashseed": config["training"]["pythonhashseed"],
        "explicit_rng_seeds": seeds,
        "configured_probabilities": ft.proportions,
        "stopping_strategy": "all_exhausted",
    }
    manifest = build_manifest(materialization=materialization, contract=contract, provenance=provenance, creation_timestamp=datetime.now(timezone.utc).isoformat())
    write_manifest(args.manifest, manifest)
    print(json.dumps({"status": "MATERIALIZED", "records": args.records, "manifest": args.manifest, **materialization}, indent=2))


if __name__ == "__main__":
    main()
