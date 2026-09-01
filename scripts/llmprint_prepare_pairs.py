"""Prepare an auditable LLMPrint pair package using the pinned external source."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
from itertools import combinations
from pathlib import Path


def load_upstream(path: Path):
    spec = importlib.util.spec_from_file_location("llmprint_generate_pairs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import pinned upstream pair source: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--tokenizer-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--num-pairs", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    from transformers import AutoTokenizer

    upstream_file = args.source / "generate_pairs.py"
    upstream = load_upstream(upstream_file)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)

    valid_by_category = {}
    for category, words in upstream.CATEGORIES.items():
        rows = []
        for word in sorted(set(words)):
            ids = tokenizer.encode(word, add_special_tokens=False)
            if len(ids) == 1:
                rows.append((word, int(ids[0])))
        if len(rows) >= 2:
            valid_by_category[category] = rows

    all_candidates = []
    for category, rows in valid_by_category.items():
        for left, right in combinations(rows, 2):
            all_candidates.append((category, left, right))
    if len(all_candidates) < args.num_pairs:
        raise RuntimeError(
            f"only {len(all_candidates)} category/single-token pairs available; "
            f"need {args.num_pairs}; candidate expansion is forbidden"
        )

    rng = random.Random(args.seed)
    categories = list(valid_by_category)
    selected = []
    seen = set()
    while len(selected) < args.num_pairs:
        category = rng.choice(categories)
        left, right = rng.sample(valid_by_category[category], 2)
        ordered = sorted((left, right), key=lambda item: item[0])
        key = (ordered[0][0], ordered[1][0])
        if key in seen:
            continue
        seen.add(key)
        selected.append(
            {
                "fingerprint_index": len(selected),
                "pair_id": f"llmprint-pair-{len(selected):03d}",
                "category": category,
                "w_plus": ordered[0][0],
                "w_minus": ordered[1][0],
                "w_plus_token_id": ordered[0][1],
                "w_minus_token_id": ordered[1][1],
            }
        )

    payload = {
        "schema_version": "wmkd.llmprint-pairs.v1",
        "upstream_source": str(upstream_file),
        "upstream_source_sha256": sha256(upstream_file),
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_revision": args.tokenizer_revision,
        "seed": args.seed,
        "requested_pairs": args.num_pairs,
        "available_candidate_pairs": len(all_candidates),
        "valid_categories": {key: len(value) for key, value in valid_by_category.items()},
        "pairs": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pairs": len(selected), "candidates": len(all_candidates), "output": str(args.output)}))


if __name__ == "__main__":
    main()
