"""Future formal entry point using a frozen SCW stream and official trainer.

The official source remains unchanged.  This wrapper replaces only the data
access function in memory, after verifying the immutable materialization.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from scw_common import OFFICIAL_COMMIT
from scw_materialized_loader import make_torch_iterable_dataset
from scw_materialized_stream import audit_materialized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-source", required=True)
    parser.add_argument("--official-runtime-config", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--custom-name", required=True)
    args = parser.parse_args()
    source = Path(args.official_source).resolve()
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != OFFICIAL_COMMIT:
        raise RuntimeError("official source commit mismatch")
    if subprocess.run(["git", "-C", str(source), "diff", "--quiet", "HEAD", "--"]).returncode or subprocess.run(["git", "-C", str(source), "diff", "--cached", "--quiet"]).returncode:
        raise RuntimeError("official tracked source must remain clean")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if os.environ.get("PYTHONHASHSEED") != str(manifest["pythonhashseed"]):
        raise RuntimeError("PYTHONHASHSEED does not match frozen stream")
    audit = audit_materialized(args.records, manifest)
    if audit["status"] != "PASS":
        raise RuntimeError(f"materialized stream audit failed: {audit['checks']}")
    sys.path.insert(0, str(source / "src"))
    import robust_fp.finetuning.finetune as official_finetune
    from robust_fp.finetuning.losses import LossTypeProcessor

    def load_frozen_stream(finetuning_config, tokenizer):
        contract = manifest["training_length_contract"]
        args_config = finetuning_config.training_args
        actual = {
            "optimizer_steps": args_config["max_steps"],
            "gradient_accumulation_steps": args_config["gradient_accumulation_steps"],
            "per_device_train_batch_size": args_config["per_device_train_batch_size"],
        }
        expected_optimizer_steps = 4 if os.environ.get("WMKD_SCW_SPEED_TEST") == "1" else contract["optimizer_steps"]
        if actual["optimizer_steps"] != expected_optimizer_steps or any(
            actual[key] != contract[key] for key in ("gradient_accumulation_steps", "per_device_train_batch_size")
        ):
            raise RuntimeError("formal training arguments differ from frozen stream contract")
        type_processor = LossTypeProcessor(device="cuda")
        type_processor.add_dataset(1, 0)
        type_processor.add_dataset(1, "anti-watermark-tv")
        type_processor.add_dataset(1, "anti-watermark-tv")
        return make_torch_iterable_dataset(args.records, args.manifest), type_processor

    official_finetune.load_datasets_from_config = load_frozen_stream
    from robust_fp import train as official_train
    official_train.main(SimpleNamespace(config=args.official_runtime_config, custom_name=args.custom_name))


if __name__ == "__main__":
    main()
