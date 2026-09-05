#!/usr/bin/env python3
"""Prepare CTCC Bb2 by changing only the experiment-level fallback gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_proactive_bb import build_config


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-config", type=Path, required=True)
    ap.add_argument("--parent-frozen20k", type=Path, required=True)
    ap.add_argument("--parent-run-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    reference = json.loads(args.reference_config.read_text(encoding="utf-8"))
    config = build_config(reference, method_slug="ctcc", parent_path=args.parent_frozen20k,
                          parent_run_id=args.parent_run_id, parent_teacher="CTCC A",
                          run_id=args.run_id, experiment="Bb2")
    before = json.loads(json.dumps(config))
    config["paraphrase"]["identity_fallback"]["enforce_full20k_max_count"] = False
    config["scientific_variant"] = {
        "name": "CTCC Experiment Bb2",
        "distinct_from": "CTCC Bb",
        "parent_blocked_run_id": "ctcc_bb_20260904_055000",
        "only_protocol_difference": "global identity-fallback-count acceptance gate is not enforced",
        "identity_fallback_fully_recorded": True,
        "per_sample_protocol_unchanged": True,
    }
    before["paraphrase"]["identity_fallback"]["enforce_full20k_max_count"] = True
    config["scientific_variant"]["reference_science_sha256_with_gate_enforced"] = digest(before)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
