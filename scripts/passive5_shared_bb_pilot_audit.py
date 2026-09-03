#!/usr/bin/env python3
"""Deterministic targeted human-audit panel for Passive-5 Shared Bb pilots."""
from __future__ import annotations

import argparse
import collections
import json
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count", type=int, default=25)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    attempts: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        attempts[row["sample_id"]].append(row)
    successes = [items[-1] for items in attempts.values() if items[-1]["status"] == "success"]
    rejected = [row for row in rows if row["status"] != "success"]
    chosen: list[dict] = []

    def add(row: dict) -> None:
        if row["sample_id"] not in {item["sample_id"] for item in chosen}:
            chosen.append(row)

    for row in successes:
        if row.get("identity_fallback"):
            add(row)
    for items in attempts.values():
        if len(items) > 1:
            add(items[-1])
    for row in successes:
        if row["sample_id"] == "qa_00454047fe5797416cb0":
            add(row)
    for row in successes:
        if not row.get("identity_fallback") and row["source_answer"].strip() == row["paraphrased_answer"].strip() and len(chosen) < 11:
            add(row)
    for row in sorted(successes, key=lambda item: len(item["source_answer"]), reverse=True)[:8]:
        add(row)
    rng = random.Random(42)
    for row in rng.sample(successes, len(successes)):
        if len(chosen) >= args.count:
            break
        add(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in chosen[: args.count]:
            source = "\n".join(line.rstrip() for line in row["source_answer"].splitlines())
            paraphrase = "\n".join(line.rstrip() for line in row["paraphrased_answer"].splitlines())
            handle.write(f"## {row['sample_id']} (attempt {row['attempt_count']})\n\n")
            handle.write(f"SOURCE:\n{source}\n\nPARAPHRASE:\n{paraphrase}\n\n")
    summary = {
        "successful_count": len(successes),
        "attempt_count": len(rows),
        "rejected_attempt_count": len(rejected),
        "retry_sample_count": sum(len(items) > 1 for items in attempts.values()),
        "final_prompt_leakage_count": sum(bool(row["quality"].get("prompt_leakage")) for row in successes),
        "final_instruction_echo_count": sum(bool(row["quality"].get("instruction_echo_leakage")) for row in successes),
        "final_control_token_leakage_count": sum(bool(row["quality"].get("chat_control_leakage")) for row in successes),
        "final_truncation_count": sum(bool(row["truncated"]) for row in successes),
        "natural_exact_copy_count": sum(not row.get("identity_fallback") and row["source_answer"].strip() == row["paraphrased_answer"].strip() for row in successes),
        "identity_fallback_count": sum(bool(row.get("identity_fallback")) for row in successes),
        "total_identity_output_count": sum(row["source_answer"].strip() == row["paraphrased_answer"].strip() for row in successes),
        "targeted_panel_count": min(len(chosen), args.count),
        "rejected_attempts": [{"sample_id": row["sample_id"], "attempt_count": row["attempt_count"],
                               "reason": row["error"], "rejected_output": row["paraphrased_answer"]} for row in rejected],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
