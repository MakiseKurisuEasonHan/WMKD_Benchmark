"""SCW finite-stream materialization contracts (CPU-safe; no remote access).

The input to :func:`materialize_records` must be the *already preprocessed and
interleaved* iterable returned by the pinned official SCW implementation.  This
is intentionally later than raw-text loading: the official implementation
tokenizes/packs each source before shuffling and probabilistic interleaving.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator

SCHEMA_VERSION = 1
SOURCE_CONTRACT = (
    {"label_id": 0, "source_dataset": "LucieFr", "role": "watermark", "loss_type": "watermark", "lambda": 1},
    {"label_id": 1, "source_dataset": "AlpacaGPT4", "role": "regularization", "loss_type": "anti-watermark-tv", "lambda": 1},
    {"label_id": 2, "source_dataset": "OpenWebText", "role": "regularization", "loss_type": "anti-watermark-tv", "lambda": 1},
)
SOURCE_BY_LABEL = {row["label_id"]: row for row in SOURCE_CONTRACT}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def training_length_contract(max_steps: int, gradient_accumulation_steps: int, batch_size: int) -> dict[str, int]:
    for value in (max_steps, gradient_accumulation_steps, batch_size):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("training length values must be positive integers")
    microbatches = max_steps * gradient_accumulation_steps
    return {
        "optimizer_steps": max_steps,
        "microbatches": microbatches,
        "per_device_train_batch_size": batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "expected_consumed_examples": microbatches * batch_size,
    }


def normalize_official_record(example: dict[str, Any], global_sample_index: int) -> dict[str, Any]:
    if set(("input_ids", "attention_mask", "labels")) - example.keys():
        raise ValueError(f"official record {global_sample_index} lacks model inputs or labels")
    input_ids = list(example["input_ids"])
    attention_mask = list(example["attention_mask"])
    if len(input_ids) != len(attention_mask) or not input_ids:
        raise ValueError(f"official record {global_sample_index} has invalid token/mask lengths")
    if any(not isinstance(token, int) for token in input_ids):
        raise ValueError(f"official record {global_sample_index} has non-integer token ids")
    if any(mask not in (0, 1) for mask in attention_mask):
        raise ValueError(f"official record {global_sample_index} has a non-binary attention mask")
    label = example["labels"]
    if hasattr(label, "item"):
        label = label.item()
    label = int(label)
    if label not in SOURCE_BY_LABEL:
        raise ValueError(f"official record {global_sample_index} has unknown label {label}")
    source = SOURCE_BY_LABEL[label]
    scientific_payload = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "label_id": label,
        "source_dataset": source["source_dataset"],
        "role": source["role"],
        "loss_type": source["loss_type"],
        "lambda": source["lambda"],
    }
    return {
        "global_sample_index": global_sample_index,
        **scientific_payload,
        "source_row_identity": None,
        "source_identity_limitation": "official preprocessing removes raw row identity before interleave",
        "content_sha256": sha256_bytes(canonical_json(scientific_payload).encode("utf-8")),
    }


def materialize_records(official_stream: Iterable[dict[str, Any]], output_path: str | Path, expected_count: int) -> dict[str, Any]:
    """Consume exactly ``expected_count`` official post-interleave examples."""
    if expected_count <= 0:
        raise ValueError("expected_count must be positive")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    sequence_digest = hashlib.sha256()
    iterator = iter(official_stream)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        for index in range(expected_count):
            try:
                record = normalize_official_record(next(iterator), index)
            except StopIteration as exc:
                raise RuntimeError(f"official stream exhausted at {index}/{expected_count}") from exc
            counts[record["source_dataset"]] += 1
            sequence_digest.update(bytes.fromhex(record["content_sha256"]))
            handle.write(canonical_json(record) + "\n")
    return {
        "materialized_record_count": expected_count,
        "source_counts": dict(counts),
        "observed_source_proportions": {name: counts[name] / expected_count for name in ("LucieFr", "AlpacaGPT4", "OpenWebText")},
        "records_file_size_bytes": output.stat().st_size,
        "records_file_sha256": file_sha256(output),
        "canonical_content_digest": sequence_digest.hexdigest(),
    }


def build_manifest(*, materialization: dict[str, Any], contract: dict[str, int], provenance: dict[str, Any], creation_timestamp: str) -> dict[str, Any]:
    if materialization["materialized_record_count"] != contract["expected_consumed_examples"]:
        raise ValueError("materialized count does not satisfy the formal training-length contract")
    return {
        "schema_version": SCHEMA_VERSION,
        "adaptation": "RUNTIME_DATA_ACCESS_ADAPTATION",
        "materialization_layer": "official_post_preprocess_post_shuffle_post_interleave_tokenized_examples",
        "creation_timestamp": creation_timestamp,
        "official_repo_commit": provenance["official_repo_commit"],
        "creation_code_version": provenance["creation_code_version"],
        "model": provenance["model"],
        "datasets": provenance["datasets"],
        "pythonhashseed": provenance["pythonhashseed"],
        "explicit_rng_seeds": provenance["explicit_rng_seeds"],
        "configured_probabilities": provenance["configured_probabilities"],
        "stopping_strategy": provenance["stopping_strategy"],
        "source_contract": list(SOURCE_CONTRACT),
        "training_length_contract": contract,
        **materialization,
        "duplicates_policy": "preserve every occurrence exactly; no deduplication",
        "source_identity_limitation": "raw source row/index is unavailable after official preprocessing; source dataset and loss identity remain exact via official label_id",
    }


def write_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def iter_materialized_records(path: str | Path, expected_manifest: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    records_path = Path(path)
    if expected_manifest and file_sha256(records_path) != expected_manifest["records_file_sha256"]:
        raise ValueError("materialized records SHA256 mismatch")
    count = 0
    with records_path.open(encoding="utf-8") as handle:
        for count, line in enumerate(handle, 1):
            stored = json.loads(line)
            record = normalize_official_record({"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["label_id"]}, count - 1)
            if stored != record:
                raise ValueError(f"materialized record mismatch at index {count - 1}")
            yield {"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["label_id"]}
    if expected_manifest and count != expected_manifest["materialized_record_count"]:
        raise ValueError("materialized record count mismatch")


def audit_materialized(records_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    sequence_digest = hashlib.sha256()
    total = 0
    record_content = True
    with Path(records_path).open(encoding="utf-8") as handle:
        for total, line in enumerate(handle, 1):
            stored = json.loads(line)
            expected = normalize_official_record({"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["label_id"]}, total - 1)
            if stored != expected:
                record_content = False
                break
            counts[stored["source_dataset"]] += 1
            sequence_digest.update(bytes.fromhex(stored["content_sha256"]))
    checks = {
        "record_content": record_content,
        "file_sha256": file_sha256(records_path) == manifest["records_file_sha256"],
        "record_count": total == manifest["materialized_record_count"],
        "source_counts": dict(counts) == manifest["source_counts"],
        "canonical_content_digest": sequence_digest.hexdigest() == manifest["canonical_content_digest"],
        "training_length_contract": total == manifest["training_length_contract"]["expected_consumed_examples"],
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
