#!/usr/bin/env python3
"""CPU-only short-answer distribution audit for the proposed Passive-5 Shared Bb2."""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

try:
    from scripts.passive5_shared_bb import atomic_json, load_config, read_jsonl, validate_source
except ModuleNotFoundError:
    from passive5_shared_bb import atomic_json, load_config, read_jsonl, validate_source

THRESHOLDS = (1, 2, 3, 4, 5, 8, 10)
BREAKDOWN_THRESHOLDS = (1, 2, 3, 5)
KNOWN_FAILURE_IDS = ("qa_00454047fe5797416cb0", "qa_027dbcaca1223ae97365")
BOOL_LIKE = {"yes", "no", "true", "false", "null", "none", "unknown", "maybe"}
COMMON_WORDS = {"tech", "dog", "spam", "classical", "boat", "human", "vehicle", "positive", "negative"}
CATEGORIES = ("single/common word", "yes/no/boolean-like", "number/numeric", "acronym",
              "proper noun / named entity-like", "code/symbol/token-like", "url/path-like",
              "short natural phrase", "other")


def percentile(values: list[int], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def category(text: str) -> str:
    stripped = text.strip()
    lowered = stripped.casefold()
    words = re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)?", stripped)
    if re.match(r"^(?:https?://|www\.|[/\\]|[A-Za-z]:[/\\])", stripped):
        return "url/path-like"
    if re.fullmatch(r"[-+]?[$£€¥]?(?:\d+(?:[.,]\d+)*|\.\d+)%?", stripped):
        return "number/numeric"
    if lowered in BOOL_LIKE:
        return "yes/no/boolean-like"
    if re.fullmatch(r"[A-Z][A-Z0-9._+-]{1,9}", stripped):
        return "acronym"
    if re.search(r"[{}\[\]<>_=;]|::|\.[A-Za-z0-9]+$", stripped) and len(words) <= 3:
        return "code/symbol/token-like"
    if len(words) == 1 and lowered in COMMON_WORDS:
        return "single/common word"
    if 1 <= len(words) <= 4 and all(word[:1].isupper() for word in words):
        return "proper noun / named entity-like"
    if len(words) == 1:
        return "single/common word"
    if 2 <= len(words) <= 6:
        return "short natural phrase"
    return "other"


def build_audit(rows: list[dict], tokenizer, source_identity: dict, tokenizer_identity: dict) -> tuple[dict, str]:
    enriched = []
    for row in rows:
        answer = row["teacher_raw_answer"]
        token_count = len(tokenizer(answer, add_special_tokens=False)["input_ids"])
        enriched.append({"sample_id": row["sample_id"], "instruction": row["instruction"],
                         "source_answer": answer, "qwen_non_special_tokens": token_count,
                         "word_count": len(re.findall(r"\S+", answer)), "char_count": len(answer),
                         "category": category(answer)})
    counts = [row["qwen_non_special_tokens"] for row in enriched]
    distribution = {
        "minimum": min(counts), "maximum": max(counts), "mean": statistics.mean(counts),
        "median": statistics.median(counts), "p25": percentile(counts, .25),
        "p75": percentile(counts, .75), "p90": percentile(counts, .90),
        "p95": percentile(counts, .95), "p99": percentile(counts, .99),
        "cumulative_thresholds": {str(t): {"count": sum(value <= t for value in counts),
                                             "percentage": 100 * sum(value <= t for value in counts) / len(counts)}
                                  for t in THRESHOLDS},
    }
    breakdown = {}
    examples = {}
    for threshold in BREAKDOWN_THRESHOLDS:
        eligible = [row for row in enriched if row["qwen_non_special_tokens"] <= threshold]
        observed = Counter(row["category"] for row in eligible)
        breakdown[str(threshold)] = {name: observed[name] for name in CATEGORIES}
        forced = [row for row in eligible if row["sample_id"] in KNOWN_FAILURE_IDS]
        selected_ids = {row["sample_id"] for row in forced}
        selected = forced + [row for row in sorted(eligible, key=lambda item: item["sample_id"])
                             if row["sample_id"] not in selected_ids][:max(0, 20 - len(forced))]
        examples[str(threshold)] = selected
    failures = []
    by_id = {row["sample_id"]: row for row in enriched}
    for sample_id in KNOWN_FAILURE_IDS:
        row = by_id[sample_id]
        failures.append({"sample_id": sample_id, "source_answer": row["source_answer"],
                         "qwen_non_special_tokens": row["qwen_non_special_tokens"],
                         "covered_by_threshold": {str(t): row["qwen_non_special_tokens"] <= t
                                                  for t in BREAKDOWN_THRESHOLDS}})
    candidate_thresholds = {}
    for threshold in BREAKDOWN_THRESHOLDS:
        identity = sum(value <= threshold for value in counts)
        candidate_thresholds[str(threshold)] = {
            "identity_preserved_count": identity, "qwen_paraphrased_count": len(rows) - identity,
            "identity_preserved_percentage": 100 * identity / len(rows),
            "covers_all_known_failures": all(item["covered_by_threshold"][str(threshold)] for item in failures),
        }
    recommended = next(t for t in BREAKDOWN_THRESHOLDS if candidate_thresholds[str(t)]["covers_all_known_failures"])
    result = {
        "schema_version": "wmkd.passive5-shared-bb2-short-answer-audit.v1",
        "status": "AUDIT_ONLY_NOT_STARTED", "source_identity": source_identity,
        "tokenizer_identity": tokenizer_identity, "token_count_definition": "add_special_tokens=false",
        "distribution": distribution, "threshold_candidates": candidate_thresholds,
        "known_failure_coverage": failures, "category_breakdown": breakdown,
        "examples": examples, "recommended_threshold": recommended,
        "recommendation_reason": "smallest candidate threshold covering every known recurrent atomic-answer failure",
        "bb2_protocol_draft": {
            "status": "NOT_YET_FROZEN", "threshold": recommended,
            "rule": "if qwen_non_special_tokens(source_answer) <= T: preserve source exactly as atomic_identity_preserve; else apply qwen_untargeted_paraphrase",
            "properties": ["detector-agnostic", "watermark-agnostic", "uniform over canonical 20k"]
        }
    }
    lines = ["# Passive-5 Shared Bb2 short-answer audit examples", "", "Status: AUDIT_ONLY_NOT_STARTED", ""]
    for threshold in BREAKDOWN_THRESHOLDS:
        lines += [f"## Qwen non-special tokens <= {threshold}", ""]
        for row in examples[str(threshold)]:
            summary = " ".join(row["instruction"].split())[:160]
            lines += [f"- `{row['sample_id']}` | tokens={row['qwen_non_special_tokens']} | words={row['word_count']} | chars={row['char_count']} | category={row['category']}",
                      f"  - Question: {summary}", f"  - Source answer: `{row['source_answer']}`"]
        lines.append("")
    return result, "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    rows = read_jsonl(args.source)
    source_identity = validate_source(rows, config, args.source)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True,
                                              revision=config["paraphraser"]["revision"])
    tokenizer_identity = {"canonical_upstream": config["paraphraser"]["canonical_upstream"],
                          "revision": config["paraphraser"]["revision"],
                          "revision_identity": config["paraphraser"]["revision_identity"],
                          "local_path": str(args.tokenizer), "vocab_size": tokenizer.vocab_size,
                          "special_token_ids": sorted(set(tokenizer.all_special_ids))}
    result, markdown = build_audit(rows, tokenizer, source_identity, tokenizer_identity)
    atomic_json(args.output_json, result)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown, encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "distribution", "threshold_candidates",
                                                   "known_failure_coverage", "recommended_threshold")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
