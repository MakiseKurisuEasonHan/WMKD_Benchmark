"""Create the immutable LLMPrint A2 first-200 pair subset manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


SOURCE_SHA256 = "47443733c5a85ee1bcb131144d2b55a4ecab44ae8de752d978d99b1119ba0c37"
TOKENIZER_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sha256(args.source) != SOURCE_SHA256:
        raise RuntimeError("source 300-pair artifact SHA256 mismatch")
    source = json.loads(args.source.read_text(encoding="utf-8"))
    selected = source["pairs"][:200]
    expected = [f"llmprint-pair-{index:03d}" for index in range(200)]
    if len(selected) != 200 or [pair["pair_id"] for pair in selected] != expected:
        raise RuntimeError("A2 subset must be exact ordered pair IDs 000-199")
    if source.get("tokenizer_revision") != TOKENIZER_REVISION:
        raise RuntimeError("tokenizer revision mismatch")
    payload = {
        "schema_version": "wmkd.llmprint-a2-pair-subset.v1",
        "experiment": "A2",
        "selection_rule": "first_200_from_frozen_300_in_original_order",
        "source_pair_artifact_sha256": SOURCE_SHA256,
        "source_pair_count": len(source["pairs"]),
        "selected_pair_count": 200,
        "selected_id_start": "llmprint-pair-000",
        "selected_id_end": "llmprint-pair-199",
        "tokenizer_path": source["tokenizer_path"],
        "tokenizer_revision": source["tokenizer_revision"],
        "seed": source["seed"],
        "pairs": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, args.output)
    print(sha256(args.output))


if __name__ == "__main__":
    main()
