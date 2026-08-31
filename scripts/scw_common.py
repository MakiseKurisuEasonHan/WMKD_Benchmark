"""CPU-only SCW Experiment A contracts and deterministic manifest helpers."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Iterable

ALPHA = 1e-3
PRIMARY_N_QUERIES = 1000
CURVE_QUERY_COUNTS = (10, 25, 50, 100, 250, 500, 1000)
CANONICAL_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
CANONICAL_REVISION = "0cb88a4f764b7a12671c53f0838cd831a0843b95"
OFFICIAL_COMMIT = "15bc1929569357130f2dbc0b09f91bbf4f4bd947"


def load_config(path: str | Path) -> dict[str, Any]:
    """The tracked .yaml is JSON-compatible YAML, avoiding local PyYAML dependency."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "project": "WMKD_Benchmark",
        "method": "SCW",
        "experiment": "A",
        "status": "NOT_RUN",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            errors.append(f"{key} must equal {value!r}")
    source, model = config["official_source"], config["model"]
    if source["commit"] != OFFICIAL_COMMIT or len(source["commit"]) != 40:
        errors.append("official source commit is not the fixed 40-character SHA")
    if model["id"] != CANONICAL_MODEL or model["revision"] != CANONICAL_REVISION:
        errors.append("canonical model/revision mismatch")
    wm, train, datasets, evaluation = (
        config["watermark"], config["training"], config["datasets"], config["evaluation"]
    )
    if wm != {"semantic_domain": "French", "type": "kgw", "gamma": 0.25, "delta": 4, "k": 1, "seeding_scheme": "simple_1"}:
        errors.append("SCW French/KGW configuration mismatch")
    required_training = {
        "mode": "full_parameter", "lora": False, "per_device_train_batch_size": 4,
        "gradient_accumulation_steps": 16, "effective_batch_size": 64,
        "learning_rate": 2e-5, "max_steps": 2500, "optimizer": "adafactor",
        "lr_scheduler_type": "cosine", "warmup_ratio": 0.1,
        "gradient_checkpointing": False, "sequence_length": 512,
    }
    for key, value in required_training.items():
        if train.get(key) != value:
            errors.append(f"training.{key} mismatch")
    if train.get("frozen_parameter_patterns") != []:
        errors.append("formal full-parameter mode cannot declare frozen parameters")
    if datasets["names"] != ["LucieFr", "AlpacaGPT4", "OpenWebText"]:
        errors.append("dataset order mismatch")
    if datasets["proportions"] != [0.6, 0.2, 0.2] or abs(sum(datasets["proportions"]) - 1.0) > 1e-12:
        errors.append("dataset proportions mismatch")
    if datasets["lambdas"] != [1, 1, 1]:
        errors.append("loss lambdas mismatch")
    if evaluation["primary_n_queries"] != PRIMARY_N_QUERIES:
        errors.append("primary query count mismatch")
    if tuple(evaluation["supplementary_query_counts"]) != CURVE_QUERY_COUNTS:
        errors.append("supplementary curve mismatch")
    if evaluation["alpha"] != ALPHA:
        errors.append("detector alpha mismatch")
    config_without_denylist = json.loads(json.dumps(config))
    config_without_denylist["safety"]["forbidden_path_fragments"] = []
    serialized = json.dumps(config_without_denylist)
    for fragment in config["safety"]["forbidden_path_fragments"]:
        if fragment in serialized:
            errors.append(f"old-project path escaped denylist: {fragment}")
    return errors


def classify_p_value(p_value: float, alpha: float = ALPHA) -> bool:
    if not 0.0 <= p_value <= 1.0:
        raise ValueError("p_value must be in [0, 1]")
    return p_value < alpha


def validate_french_rows(rows: Iterable[dict[str, Any]], expected_count: int | None = None) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_index, row in enumerate(rows):
        if set(("instruction", "output")) - row.keys():
            raise ValueError(f"row {source_index} lacks instruction/output")
        instruction, output = row["instruction"], row["output"]
        if not isinstance(instruction, str) or not instruction.strip() or not isinstance(output, str) or not output.strip():
            raise ValueError(f"row {source_index} has empty/non-string fields")
        identity = canonical_json_sha256({"source_index": source_index, "instruction": instruction, "output": output})
        if identity in seen:
            raise ValueError(f"duplicate stable identity at row {source_index}")
        seen.add(identity)
        validated.append({"source_index": source_index, "sample_id": identity, "instruction": instruction, "output": output})
    if expected_count is not None and len(validated) != expected_count:
        raise ValueError(f"expected {expected_count} rows, got {len(validated)}")
    return validated


def fixed_permutation(size: int, seed: int) -> list[int]:
    if size < PRIMARY_N_QUERIES:
        raise ValueError(f"primary SCW evaluation requires at least {PRIMARY_N_QUERIES} rows")
    indices = list(range(size))
    random.Random(seed).shuffle(indices)
    return indices


def flatten_padded(token_rows: list[list[int]], mask_rows: list[list[int]], indices: list[int]) -> tuple[list[int], list[int]]:
    if len(token_rows) != len(mask_rows):
        raise ValueError("token/mask row count mismatch")
    flat_tokens: list[int] = []
    flat_masks: list[int] = []
    width: int | None = None
    for index in indices:
        tokens, masks = token_rows[index], mask_rows[index]
        if len(tokens) != len(masks):
            raise ValueError(f"token/mask width mismatch at row {index}")
        width = len(tokens) if width is None else width
        if len(tokens) != width:
            raise ValueError("official aggregation requires tokenizer padding to a common width")
        if any(value not in (0, 1) for value in masks):
            raise ValueError("attention mask must be binary")
        flat_tokens.extend(tokens)
        flat_masks.extend(masks)
    return flat_tokens, flat_masks


def curve_from_pvalues(pvalues: dict[int, float]) -> list[dict[str, Any]]:
    if tuple(sorted(pvalues)) != CURVE_QUERY_COUNTS:
        raise ValueError("curve must contain exactly the fixed supplementary query counts")
    return [{"n_queries": n, "p_value": pvalues[n], "fingerprinted": classify_p_value(pvalues[n]), "supplementary": True} for n in CURVE_QUERY_COUNTS]
