#!/usr/bin/env python3
"""Freeze teacher QA candidates for paired Ba/Bb use.

Formal model inference is intentionally a separate, approval-gated stage. This command
preserves and freezes already generated raw candidates deterministically.
"""

import argparse
import json
from pathlib import Path

try:
    from scripts.distillation_data import freeze_candidates, read_jsonl, write_jsonl
except ModuleNotFoundError:  # direct execution from scripts/
    from distillation_data import freeze_candidates, read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-candidates", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--target-count", type=int, default=20_000)
    parser.add_argument("--provenance", required=True, help="JSON provenance/config file")
    args = parser.parse_args()
    candidates = read_jsonl(args.raw_candidates)
    frozen, manifest = freeze_candidates(candidates, args.target_count)
    provenance = json.loads(Path(args.provenance).read_text(encoding="utf-8"))
    manifest["provenance"] = provenance
    write_jsonl(args.output, frozen)
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "frozen", "samples": len(frozen), "dataset_sha256": manifest["dataset_sha256"]}))


if __name__ == "__main__":
    main()
