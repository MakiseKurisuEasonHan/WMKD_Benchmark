#!/usr/bin/env python3
"""Local-safe primitives and future runtime entry points for Passive-5 Shared Bb."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import statistics
from pathlib import Path
from typing import Callable, Iterable

REQUIRED_SOURCE = ("sample_id", "instruction", "input", "teacher_raw_answer")
REQUIRED_PAIR = (
    "sample_id", "source_question", "source_answer", "source_answer_sha256",
    "paraphrased_answer", "paraphrased_answer_sha256", "source_answer_token_count",
    "paraphrased_answer_token_count", "generation_config_identity",
    "paraphrase_prompt_identity", "status", "attempt_count", "finish_reason",
    "truncated", "error",
)
UNRESOLVED_REVISIONS = {"", "REQUIRED", "TBD", "REQUIRED_TBD", None}


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def records_sha256(records: Iterable[dict]) -> str:
    digest = hashlib.sha256()
    for row in records:
        digest.update(canonical_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def read_jsonl(path: str | Path) -> list[dict]:
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
    return rows


def atomic_json(path: str | Path, value: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def atomic_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)


def append_jsonl_durable(path: str | Path, row: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_config(path: str | Path) -> dict:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    prompt = Path(path).parents[2] / config["paraphrase"]["prompt_path"]
    if file_sha256(prompt) != config["paraphrase"]["prompt_sha256"]:
        raise ValueError("FAIL_CLOSED_PARAPHRASE_PROMPT_HASH_MISMATCH")
    return config


def validate_source(rows: list[dict], config: dict, file_path: str | Path | None = None) -> dict:
    expected = config["source_dataset"]
    if len(rows) != expected["record_count"]:
        raise ValueError(f"SOURCE_COUNT_MISMATCH expected={expected['record_count']} observed={len(rows)}")
    ids = []
    for index, row in enumerate(rows):
        missing = [field for field in REQUIRED_SOURCE if field not in row]
        if missing:
            raise ValueError(f"SOURCE_SCHEMA_MISMATCH index={index} missing={missing}")
        if not str(row["sample_id"]).strip() or not str(row["instruction"]).strip() or not str(row["teacher_raw_answer"]).strip():
            raise ValueError(f"SOURCE_EMPTY_REQUIRED_FIELD index={index}")
        ids.append(row["sample_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_SOURCE_SAMPLE_ID")
    dataset_sha = records_sha256(rows)
    ids_sha = records_sha256([{"sample_id": sample_id} for sample_id in ids])
    if dataset_sha != expected["dataset_sha256"]:
        raise ValueError(f"SOURCE_DATASET_HASH_MISMATCH observed={dataset_sha}")
    if ids_sha != expected["sample_ids_sha256"]:
        raise ValueError(f"SOURCE_SAMPLE_IDS_HASH_MISMATCH observed={ids_sha}")
    observed_file_sha = file_sha256(file_path) if file_path else None
    if observed_file_sha and observed_file_sha != expected["frozen_jsonl_sha256"]:
        raise ValueError(f"SOURCE_FILE_HASH_MISMATCH observed={observed_file_sha}")
    return {"status": "PASS", "record_count": len(rows), "dataset_sha256": dataset_sha,
            "sample_ids_sha256": ids_sha, "frozen_jsonl_sha256": observed_file_sha}


def generation_identity(config: dict) -> str:
    fields = {key: config["paraphrase"][key] for key in ("do_sample", "temperature", "top_p", "seed", "dynamic_max_new_tokens")}
    fields["paraphraser"] = {key: config["paraphraser"][key] for key in ("canonical_upstream", "revision", "revision_identity")}
    return text_sha256(canonical_json(fields))


def dynamic_budget(source_tokens: int, policy: dict) -> int:
    return min(int(policy["global_cap"]), max(int(policy["min_cap"]), math.ceil(source_tokens * float(policy["multiplier"]))))


def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def lexical_change(source: str, paraphrase: str) -> float:
    left, right = set(tokens(source)), set(tokens(paraphrase))
    return 0.0 if not left and not right else 1.0 - len(left & right) / max(1, len(left | right))


def quality_flags(source: str, paraphrase: str, finish_reason: str | None, config: dict) -> dict:
    q = config["quality"]
    source_words, para_words = tokens(source), tokens(paraphrase)
    ratio = len(para_words) / max(1, len(source_words))
    lowered = paraphrase.casefold()
    source_lowered = source.casefold()
    leakage = [marker for marker in q["prompt_leakage_markers"] if marker.casefold() in lowered]
    instruction_echoes = [phrase for phrase in q["instruction_echo_phrases"]
                          if phrase.casefold() in lowered and phrase.casefold() not in source_lowered]
    controls = [marker for marker in q["chat_control_markers"] if marker.casefold() in lowered]
    change = lexical_change(source, paraphrase)
    truncated = finish_reason in {"length", "max_tokens", "max_new_tokens"}
    failures = []
    diagnostics = []
    if not paraphrase.strip(): failures.append("empty_output")
    if source.strip() == paraphrase.strip(): diagnostics.append("exact_copy")
    if leakage: failures.append("prompt_leakage")
    if instruction_echoes: failures.append("instruction_echo_leakage")
    if controls: failures.append("chat_control_token_leakage")
    if truncated: failures.append("truncated")
    if not q["length_ratio_min"] <= ratio <= q["length_ratio_max"]: diagnostics.append("length_ratio_out_of_bounds")
    if change < q["minimum_lexical_change"]: diagnostics.append("insufficient_lexical_change")
    return {"pass": not failures, "failures": failures, "diagnostics": diagnostics, "length_ratio": ratio,
            "lexical_change": change, "prompt_leakage": leakage, "instruction_echo_leakage": instruction_echoes,
            "chat_control_leakage": controls,
            "truncated": truncated, "semantic_similarity": None}


def source_question(row: dict) -> str:
    return row["instruction"] + (("\n\nInput:\n" + row["input"]) if row.get("input") else "")


def build_pair(row: dict, answer: str, source_token_count: int, paraphrase_token_count: int,
               attempt: int, finish_reason: str | None, error: str | None, config: dict) -> dict:
    flags = quality_flags(row["teacher_raw_answer"], answer, finish_reason, config)
    status = "success" if not error and flags["pass"] else "failed"
    return {
        "sample_id": row["sample_id"], "instruction": row["instruction"], "input": row["input"],
        "source_question": source_question(row), "source_answer": row["teacher_raw_answer"],
        "source_answer_sha256": text_sha256(row["teacher_raw_answer"]),
        "paraphrased_answer": answer.strip(), "paraphrased_answer_sha256": text_sha256(answer.strip()),
        "source_answer_token_count": source_token_count, "paraphrased_answer_token_count": paraphrase_token_count,
        "generation_config_identity": generation_identity(config),
        "paraphrase_prompt_identity": config["paraphrase"]["prompt_sha256"],
        "status": status, "attempt_count": attempt, "finish_reason": finish_reason,
        "truncated": flags["truncated"], "error": error or (";".join(flags["failures"]) if flags["failures"] else None),
        "quality": flags, "identity_fallback": False, "fallback_reason": None,
        "failed_attempt_count": 0, "rejected_attempts": [],
    }


def build_identity_fallback(row: dict, source_token_count: int, attempt: int,
                            rejected: list[dict], config: dict) -> dict:
    """Create an auditable, byte-preserving source-answer fallback after retries."""
    answer = row["teacher_raw_answer"]
    flags = quality_flags(answer, answer, "identity_fallback", config)
    reason = config["paraphrase"]["identity_fallback"]["reason"]
    return {
        "sample_id": row["sample_id"], "instruction": row["instruction"], "input": row["input"],
        "source_question": source_question(row), "source_answer": answer,
        "source_answer_sha256": text_sha256(answer), "paraphrased_answer": answer,
        "paraphrased_answer_sha256": text_sha256(answer),
        "source_answer_token_count": source_token_count,
        "paraphrased_answer_token_count": source_token_count,
        "generation_config_identity": generation_identity(config),
        "paraphrase_prompt_identity": config["paraphrase"]["prompt_sha256"],
        "status": "success", "attempt_count": attempt, "finish_reason": "identity_fallback",
        "truncated": False, "error": None, "quality": flags, "identity_fallback": True,
        "fallback_reason": reason, "failed_attempt_count": len(rejected),
        "rejected_attempts": [{"attempt_count": item["attempt_count"],
                               "rejected_output": item["paraphrased_answer"],
                               "rejection_reason": item["error"]} for item in rejected],
        "final_answer": answer, "final_answer_sha256": text_sha256(answer),
    }


def load_attempts(path: str | Path, source_by_id: dict[str, dict]) -> tuple[list[dict], dict[str, dict], dict[str, int]]:
    journal = read_jsonl(path) if Path(path).exists() else []
    successes: dict[str, dict] = {}
    counts: dict[str, int] = {}
    seen_attempts = set()
    for record in journal:
        sample_id, attempt = record.get("sample_id"), record.get("attempt_count")
        if sample_id not in source_by_id: raise ValueError(f"UNKNOWN_JOURNAL_SAMPLE_ID {sample_id}")
        key = (sample_id, attempt)
        if key in seen_attempts: raise ValueError(f"DUPLICATE_SAMPLE_ATTEMPT {key}")
        seen_attempts.add(key)
        source = source_by_id[sample_id]["teacher_raw_answer"]
        if record.get("source_answer_sha256") != text_sha256(source): raise ValueError(f"SOURCE_HASH_MISMATCH {sample_id}")
        counts[sample_id] = max(counts.get(sample_id, 0), int(attempt))
        if record.get("status") == "success":
            if sample_id in successes: raise ValueError(f"DUPLICATE_SUCCESS_SAMPLE_ID {sample_id}")
            successes[sample_id] = record
    return journal, successes, counts


def run_records(source: list[dict], journal_path: str | Path, config: dict,
                generator: Callable, limit: int | None = None) -> dict:
    source_by_id = {row["sample_id"]: row for row in source}
    journal, successes, counts = load_attempts(journal_path, source_by_id)
    maximum = config["paraphrase"]["retry"]["maximum_attempts_per_sample"]
    fallback_config = config["paraphrase"].get("identity_fallback", {})
    processed = 0
    for row in source:
        sample_id = row["sample_id"]
        if sample_id in successes: continue
        while counts.get(sample_id, 0) < maximum and sample_id not in successes:
            attempt = counts.get(sample_id, 0) + 1
            approximate_source_tokens = len(tokens(row["teacher_raw_answer"]))
            generated = generator(row, attempt, dynamic_budget(approximate_source_tokens, config["paraphrase"]["dynamic_max_new_tokens"]))
            if len(generated) == 4: answer, para_tokens, finish_reason, error = generated; source_tokens = approximate_source_tokens
            else: answer, para_tokens, finish_reason, error, source_tokens = generated
            record = build_pair(row, answer, source_tokens, para_tokens, attempt, finish_reason, error, config)
            journal.append(record); counts[sample_id] = attempt
            append_jsonl_durable(journal_path, record)
            if record["status"] == "success": successes[sample_id] = record
            atomic_json(Path(journal_path).with_name("progress.json"), {
                "source_count": len(source), "successful_count": len(successes),
                "attempt_records": len(journal), "current_sample_id": sample_id,
                "complete": len(successes) == len(source),
            })
        if sample_id not in successes and counts.get(sample_id, 0) >= maximum and fallback_config.get("enabled"):
            rejected = [item for item in journal if item["sample_id"] == sample_id and item["status"] != "success"]
            approximate_source_tokens = rejected[-1]["source_answer_token_count"] if rejected else len(tokens(row["teacher_raw_answer"]))
            record = build_identity_fallback(row, approximate_source_tokens, maximum + 1, rejected, config)
            journal.append(record); counts[sample_id] = maximum + 1; successes[sample_id] = record
            append_jsonl_durable(journal_path, record)
            fallback_count = sum(bool(item.get("identity_fallback")) for item in successes.values())
            if fallback_count > int(fallback_config["full20k_max_count"]):
                raise RuntimeError(f"IDENTITY_FALLBACK_AGGREGATE_GATE count={fallback_count} max={fallback_config['full20k_max_count']}")
        processed += 1
        if limit is not None and processed >= limit: break
    exhausted = [sid for sid in source_by_id if sid not in successes and counts.get(sid, 0) >= maximum]
    fallback_count = sum(bool(row.get("identity_fallback")) for row in successes.values())
    progress = {"source_count": len(source), "successful_count": len(successes), "attempt_records": len(journal),
                "generation_retry_count": sum(max(0, min(int(row["attempt_count"]), maximum) - 1) for row in successes.values()),
                "retry_count": len(journal) - len({row["sample_id"] for row in journal}),
                "identity_fallback_count": fallback_count, "exhausted_sample_ids": exhausted,
                "complete": len(successes) == len(source)}
    atomic_json(Path(journal_path).with_name("progress.json"), progress)
    if exhausted: raise RuntimeError(f"PARAPHRASE_RETRY_EXHAUSTED count={len(exhausted)}")
    return progress


def freeze(source: list[dict], journal_path: str | Path, output: str | Path, config: dict) -> dict:
    if Path(output).exists() or Path(output).with_suffix(".manifest.json").exists():
        raise FileExistsError(f"OUTPUT_COLLISION {output}")
    source_by_id = {row["sample_id"]: row for row in source}
    _, successes, _ = load_attempts(journal_path, source_by_id)
    if len(successes) != len(source) or len(source) != config["source_dataset"]["record_count"]:
        raise RuntimeError(f"FAIL_CLOSED_EXACT_COUNT successes={len(successes)} source={len(source)}")
    ordered = [successes[row["sample_id"]] for row in source]
    for record in ordered:
        missing = [field for field in REQUIRED_PAIR if field not in record]
        if missing or record["status"] != "success": raise ValueError(f"PAIR_SCHEMA_OR_STATUS_FAILURE {record.get('sample_id')} {missing}")
    atomic_jsonl(output, ordered)
    manifest = {"schema_version": "wmkd.passive5-shared-bb-paired-dataset.v1", "sample_count": len(ordered),
                "source_dataset_sha256": config["source_dataset"]["dataset_sha256"],
                "sample_ids_sha256": records_sha256([{"sample_id": row["sample_id"]} for row in ordered]),
                "paired_dataset_sha256": records_sha256(ordered), "frozen_jsonl_sha256": file_sha256(output),
                "generation_config_identity": generation_identity(config), "prompt_sha256": config["paraphrase"]["prompt_sha256"]}
    atomic_json(Path(output).with_suffix(".manifest.json"), manifest)
    return manifest


def audit(pairs: list[dict], output_dir: str | Path, config: dict) -> dict:
    if not pairs: raise ValueError("EMPTY_PAIR_DATASET")
    ratios = [row["quality"]["length_ratio"] for row in pairs]
    changes = [row["quality"]["lexical_change"] for row in pairs]
    identity_fallback_count = sum(bool(row.get("identity_fallback")) for row in pairs)
    natural_exact_copy_count = sum(not row.get("identity_fallback") and row["source_answer"].strip() == row["paraphrased_answer"].strip() for row in pairs)
    total_identity_output_count = sum(row["source_answer"].strip() == row["paraphrased_answer"].strip() for row in pairs)
    result = {"sample_count": len(pairs), "exact_copy_count": total_identity_output_count,
              "exact_copy_rate": total_identity_output_count / len(pairs),
              "natural_exact_copy_count": natural_exact_copy_count,
              "identity_fallback_count": identity_fallback_count,
              "identity_fallback_rate": identity_fallback_count / len(pairs),
              "total_identity_output_count": total_identity_output_count,
              "mean_length_ratio": statistics.mean(ratios), "median_length_ratio": statistics.median(ratios),
              "truncation_count": sum(bool(row["truncated"]) for row in pairs),
              "prompt_leakage_count": sum(bool(row["quality"].get("prompt_leakage")) for row in pairs),
              "instruction_echo_leakage_count": sum(bool(row["quality"].get("instruction_echo_leakage")) for row in pairs),
              "chat_control_leakage_count": sum(bool(row["quality"].get("chat_control_leakage")) for row in pairs),
              "generation_failure_count": sum(row["status"] != "success" for row in pairs),
              "retry_count": sum(max(0, int(row["attempt_count"]) - 1) for row in pairs),
              "mean_lexical_change": statistics.mean(changes), "median_lexical_change": statistics.median(changes),
              "semantic_similarity": "not_recorded_optional_hook_disabled"}
    out = Path(output_dir); atomic_json(out / "quality_audit.json", result)
    rng = random.Random(config["paraphrase"]["seed"])
    sample = rng.sample(pairs, min(config["quality"]["human_audit_sample_count"], len(pairs)))
    text = "\n\n".join(f"## {row['sample_id']}\n\nSOURCE:\n{row['source_answer']}\n\nPARAPHRASE:\n{row['paraphrased_answer']}" for row in sample)
    (out / "human_audit_samples.md").write_text(text + "\n", encoding="utf-8")
    return result


def audit_journal(source: list[dict], journal_path: str | Path, output_dir: str | Path, config: dict) -> dict:
    _, successes, _ = load_attempts(journal_path, {row["sample_id"]: row for row in source})
    ordered = [successes[row["sample_id"]] for row in source if row["sample_id"] in successes]
    result = audit(ordered, output_dir, config)
    result["pilot_or_partial"] = len(ordered) != len(source)
    atomic_json(Path(output_dir) / "quality_audit.json", result)
    return result


def adapt_student_dataset(pairs: list[dict], output: str | Path) -> dict:
    rows = [{"sample_id": row["sample_id"], "instruction": row["instruction"], "input": row["input"],
             "teacher_raw_answer": row["paraphrased_answer"]} for row in pairs]
    atomic_jsonl(output, rows)
    return {"sample_count": len(rows), "dataset_sha256": records_sha256(rows), "file_sha256": file_sha256(output),
            "target_semantics": "UP_paraphrased_answer adapted to existing teacher_raw_answer trainer field"}


def validate_training_parity(ba: dict, bb: dict) -> dict:
    shared = ("epochs", "learning_rate", "precision", "full_parameter", "lora", "per_device_batch_size",
              "gradient_accumulation_steps", "effective_batch_size", "max_length", "optimizer", "scheduler",
              "warmup_ratio", "weight_decay", "expected_steps", "checkpoint_retention")
    mismatches = {key: {"ba": ba["training"].get(key), "bb": bb["training"].get(key)} for key in shared if ba["training"].get(key) != bb["training"].get(key)}
    student_keys = ("model_id", "revision", "initialization", "resume")
    mismatches.update({f"student.{key}": {"ba": ba["student"].get(key), "bb": bb["student"].get(key)} for key in student_keys if ba["student"].get(key) != bb["student"].get(key)})
    if mismatches: raise ValueError(f"BA_BB_TRAINING_PARITY_MISMATCH {mismatches}")
    if bb["student"]["revision"] != "0cb88a4f764b7a12671c53f0838cd831a0843b95": raise ValueError("WRONG_STUDENT_REVISION")
    return {"status": "PASS", "fields_checked": list(shared) + [f"student.{key}" for key in student_keys]}


def planning_full_log(config: dict) -> dict:
    return {"schema_version": "wmkd.full-experiment-log.v1",
            "identity": {"experiment": "Passive-5 Shared Bb", "run_id": None, "shared_attack": True},
            "parent_experiment": {"experiment": "Passive-5 Shared Ba", "run_id": config["source_dataset"]["parent_run_id"]},
            "status": "PREPARED_NOT_STARTED", "provenance": {"config": "configs/distillation/passive5_shared_bb.json"},
            "environment": None, "source_dataset": config["source_dataset"], "paraphraser": config["paraphraser"],
            "paraphrase_config": config["paraphrase"], "paraphrase_telemetry": None, "paraphrase_quality": None,
            "student_initialization": config["student"], "student_training": config["training"], "training_telemetry": None,
            "detectors": {"configuration": config["detectors"], "results": None}, "utility": {"configuration": config["utility"], "results": None},
            "artifacts": {}, "failures": [], "continuations": [],
            "analysis_support": {"checkpoint_level_detector_trajectory": False}, "bounded_conclusion": None}


FULL_LOG_REQUIRED = ("schema_version", "identity", "parent_experiment", "status", "provenance", "environment",
    "source_dataset", "paraphraser", "paraphrase_config", "paraphrase_telemetry", "paraphrase_quality",
    "student_initialization", "student_training", "training_telemetry", "detectors", "utility", "artifacts",
    "failures", "continuations", "analysis_support", "bounded_conclusion")


def validate_full_log(value: dict) -> dict:
    missing = [field for field in FULL_LOG_REQUIRED if field not in value]
    if missing: raise ValueError(f"FULL_LOG_SCHEMA_MISSING {missing}")
    if value["schema_version"] != "wmkd.full-experiment-log.v1": raise ValueError("FULL_LOG_SCHEMA_VERSION")
    if value["status"] not in {"PREPARED_NOT_STARTED", "RUNNING", "FAILED", "COMPLETED"}: raise ValueError("FULL_LOG_STATUS")
    return {"status": "PASS", "fields_checked": len(FULL_LOG_REQUIRED)}


def update_global_index(index_path: str | Path, full_log_path: str | Path, relative_path: str, entry: dict) -> dict:
    full_log = json.loads(Path(full_log_path).read_text(encoding="utf-8")); validate_full_log(full_log)
    if full_log["status"] != "COMPLETED": raise ValueError("INDEX_REQUIRES_COMPLETED_FULL_LOG")
    index = json.loads(Path(index_path).read_text(encoding="utf-8"))
    if any(row.get("full_log_path") == relative_path or (row.get("experiment") == "Bb" and row.get("run_id") == entry.get("run_id")) for row in index["objects"]):
        raise ValueError("GLOBAL_INDEX_COLLISION")
    row = {**entry, "experiment": "Bb", "shared_attack": True, "full_log_path": relative_path,
           "full_log_sha256": file_sha256(full_log_path)}
    index["objects"].append(row); index["object_count"] = len(index["objects"])
    atomic_json(index_path, index)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("validate-source"); s.add_argument("--source", required=True)
    p = sub.add_parser("parity"); p.add_argument("--ba-config", required=True)
    l = sub.add_parser("planning-log"); l.add_argument("--output", required=True)
    f = sub.add_parser("freeze"); f.add_argument("--source", required=True); f.add_argument("--journal", required=True); f.add_argument("--output", required=True)
    q = sub.add_parser("quality-audit"); q.add_argument("--pairs", required=True); q.add_argument("--output-dir", required=True)
    j = sub.add_parser("audit-journal"); j.add_argument("--source", required=True); j.add_argument("--journal", required=True); j.add_argument("--output-dir", required=True)
    d = sub.add_parser("adapt-student"); d.add_argument("--pairs", required=True); d.add_argument("--output", required=True)
    args = parser.parse_args(); config = load_config(args.config)
    if args.command == "validate-source": print(json.dumps(validate_source(read_jsonl(args.source), config, args.source), indent=2))
    elif args.command == "parity": print(json.dumps(validate_training_parity(json.loads(Path(args.ba_config).read_text()), config), indent=2))
    elif args.command == "planning-log":
        value = planning_full_log(config); validate_full_log(value); atomic_json(args.output, value)
    elif args.command == "freeze": print(json.dumps(freeze(read_jsonl(args.source), args.journal, args.output, config), indent=2))
    elif args.command == "quality-audit": print(json.dumps(audit(read_jsonl(args.pairs), args.output_dir, config), indent=2))
    elif args.command == "audit-journal": print(json.dumps(audit_journal(read_jsonl(args.source), args.journal, args.output_dir, config), indent=2))
    elif args.command == "adapt-student": print(json.dumps(adapt_student_dataset(read_jsonl(args.pairs), args.output), indent=2))


if __name__ == "__main__": main()
