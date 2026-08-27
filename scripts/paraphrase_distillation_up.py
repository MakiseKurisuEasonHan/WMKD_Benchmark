#!/usr/bin/env python3
"""Answer-only Dipper UP with failure preservation and strict paired validation."""

import argparse
import json
from pathlib import Path

try:
    from scripts.distillation_data import read_jsonl, validate_up_pair, write_jsonl
except ModuleNotFoundError:  # direct execution from scripts/
    from distillation_data import read_jsonl, validate_up_pair, write_jsonl


def build_record(source: dict, answer: str | None, error: str | None = None) -> dict:
    return {
        **source,
        "UP_paraphrased_answer": (answer or "").strip(),
        "paraphrase_status": "success" if answer and answer.strip() and not error else "failed",
        "paraphrase_error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--failure-log", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--lex-diversity", type=int, default=60)
    parser.add_argument("--order-diversity", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--mock-answers", help="CPU-test JSON mapping sample_id to paraphrase")
    args = parser.parse_args()
    source = read_jsonl(args.input)
    mock = json.loads(Path(args.mock_answers).read_text(encoding="utf-8")) if args.mock_answers else None
    if mock is None:
        raise SystemExit("Formal Dipper execution is approval-gated; provide --mock-answers only for CPU tests")
    output = []
    failures = []
    for record in source:
        answer = mock.get(record["sample_id"])
        item = build_record(record, answer, None if answer else "missing_mock_answer")
        output.append(item)
        if item["paraphrase_status"] != "success":
            failures.append({"sample_id": record["sample_id"], "error": item["paraphrase_error"]})
    write_jsonl(args.output, output)
    Path(args.failure_log).write_text(json.dumps(failures, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise RuntimeError(f"{len(failures)} paraphrases failed; no samples were dropped")
    validate_up_pair(source, output)


if __name__ == "__main__":
    main()
