#!/usr/bin/env python3
"""Deterministic, paired dataset primitives for PN-FP Ba/Bb."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


REQUIRED_FROZEN = ("sample_id", "instruction", "input", "teacher_raw_answer")


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_sample_id(instruction: str, input_text: str) -> str:
    payload = canonical_json({"instruction": instruction.strip(), "input": input_text.strip()})
    return "qa_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def records_sha256(records: Iterable[dict]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(canonical_json(record).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def freeze_candidates(candidates: Iterable[dict], target_count: int) -> tuple[list[dict], dict]:
    """Normalize, filter and deduplicate without depending on input ordering side effects."""
    accepted: dict[str, dict] = {}
    rejected = []
    for index, candidate in enumerate(candidates):
        instruction = str(candidate.get("instruction", "")).strip()
        input_text = str(candidate.get("input", "")).strip()
        answer = str(candidate.get("teacher_raw_answer", candidate.get("answer", ""))).strip()
        if not instruction or not answer:
            rejected.append({"candidate_index": index, "reason": "empty_instruction_or_answer"})
            continue
        sample_id = stable_sample_id(instruction, input_text)
        if sample_id in accepted:
            rejected.append({"candidate_index": index, "sample_id": sample_id, "reason": "duplicate_task"})
            continue
        accepted[sample_id] = {
            "sample_id": sample_id,
            "instruction": instruction,
            "input": input_text,
            "teacher_raw_answer": answer,
        }
    frozen = [accepted[key] for key in sorted(accepted)]
    if len(frozen) < target_count:
        raise ValueError(f"only {len(frozen)} valid unique samples; {target_count} required")
    frozen = frozen[:target_count]
    manifest = {
        "schema_version": 1,
        "sample_count": len(frozen),
        "sample_ids_sha256": records_sha256([{"sample_id": r["sample_id"]} for r in frozen]),
        "dataset_sha256": records_sha256(frozen),
        "rejected_count": len(rejected),
        "rejections": rejected,
    }
    return frozen, manifest


def validate_up_pair(source: list[dict], paraphrased: list[dict]) -> None:
    if len(source) != len(paraphrased):
        raise ValueError("UP sample count changed")
    for index, (raw, up) in enumerate(zip(source, paraphrased)):
        for field in ("sample_id", "instruction", "input"):
            if raw.get(field) != up.get(field):
                raise ValueError(f"UP mutated {field} at index {index}")
        if not str(up.get("UP_paraphrased_answer", "")).strip():
            raise ValueError(f"empty UP answer at index {index}")
        if up.get("paraphrase_status") != "success":
            raise ValueError(f"non-success UP record at index {index}")
