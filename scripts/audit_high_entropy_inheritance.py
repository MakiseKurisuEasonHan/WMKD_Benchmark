#!/usr/bin/env python3
"""Report hashes and provenance of high-entropy candidates without emitting text."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
from pathlib import Path

PATTERN = re.compile(r"\b[A-Za-z0-9+/=_-]{32,}\b")
FIELDS = ("instruction", "input", "source_answer", "paraphrased_answer")


def entropy(value: str) -> float:
    counts = collections.Counter(value)
    size = len(value)
    return -sum((count / size) * math.log2(count / size) for count in counts.values())


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--processed", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    parent = {row["sample_id"]: row for row in read_jsonl(args.parent)}
    findings = []
    for row in read_jsonl(args.processed):
        inherited_values = (
            str(parent[row["sample_id"]].get(key, ""))
            for key in ("instruction", "input", "teacher_raw_answer")
        )
        inherited_values = tuple(inherited_values)
        for field in FIELDS:
            for candidate in PATTERN.findall(str(row.get(field, ""))):
                score = entropy(candidate)
                if score < 4.5:
                    continue
                findings.append({
                    "sample_id": row["sample_id"],
                    "field": field,
                    "length": len(candidate),
                    "entropy": round(score, 6),
                    "sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                    "identical_in_parent_record": any(
                        candidate in value for value in inherited_values
                    ),
                })
    result = {
        "candidate_count": len(findings),
        "all_candidates_identical_in_parent_record": all(
            row["identical_in_parent_record"] for row in findings
        ),
        "candidate_text_emitted": False,
        "findings": findings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
