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
            if expected_manifest and expected_manifest.get("adaptation") == "SCW_A2_WMKD_DOMESTIC_DATA_80K_UNIQUE_TWO_PASS":
                if stored.get("global_index") != count - 1 or stored.get("official_label") != stored.get("source_schedule_label"):
                    raise ValueError(f"A2 index/schedule mismatch at {count - 1}")
                yield {"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["official_label"]}
                continue
            if expected_manifest and expected_manifest.get("adaptation") == "DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION":
                if stored.get("global_index") != count - 1 or stored.get("official_label") != stored.get("source_schedule_label"):
                    raise ValueError(f"deterministic finite-stream index/schedule mismatch at {count - 1}")
                source = SOURCE_BY_LABEL.get(stored["official_label"])
                if source is None or stored.get("source_dataset") != source["source_dataset"] or stored.get("loss_type") != source["loss_type"] or stored.get("lambda") != source["lambda"]:
                    raise ValueError(f"deterministic finite-stream source contract mismatch at {count - 1}")
                yield {"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["official_label"]}
                continue
            record = normalize_official_record({"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["label_id"]}, count - 1)
            if stored != record:
                raise ValueError(f"materialized record mismatch at index {count - 1}")
            yield {"input_ids": stored["input_ids"], "attention_mask": stored["attention_mask"], "labels": stored["label_id"]}
    if expected_manifest and count != expected_manifest["materialized_record_count"]:
        raise ValueError("materialized record count mismatch")


def audit_materialized(records_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("adaptation") == "SCW_A2_WMKD_DOMESTIC_DATA_80K_UNIQUE_TWO_PASS":
        return audit_a2_frozen80k(records_path, manifest)
    if manifest.get("adaptation") == "DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION":
        return audit_deterministic_finite_stream(records_path, manifest)
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


def audit_a2_frozen80k(records_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    schedule=list(Path(manifest["source_schedule_path"]).read_bytes()); expected_names=("AyaFrench","MSInstruct","MSOpenWebText"); expected_losses=("watermark","anti-watermark-tv","anti-watermark-tv")
    counts=Counter(); local=Counter(); identities=set(); digest=hashlib.sha256(); total=0; valid=True
    with Path(records_path).open(encoding="utf-8") as handle:
        for total,line in enumerate(handle,1):
            row=json.loads(line); index=total-1
            if index>=len(schedule): valid=False; break
            role=schedule[index]
            if row.get("global_index")!=index or row.get("source_schedule_label")!=role or row.get("official_label")!=role or row.get("source_local_index")!=local[role]: valid=False; break
            if row.get("source_dataset")!=expected_names[role] or row.get("loss_type")!=expected_losses[role] or row.get("lambda")!=1: valid=False; break
            ids=row.get("input_ids"); mask=row.get("attention_mask"); identity=(role,canonical_json(row.get("source_identity")))
            if not isinstance(ids,list) or len(ids)!=512 or len(mask)!=512 or identity in identities: valid=False; break
            payload={k:row[k] for k in ("input_ids","attention_mask","official_label","source_dataset","loss_type","lambda","source_identity")}; content=sha256_bytes(canonical_json(payload).encode())
            if content!=row.get("content_sha256"): valid=False; break
            identities.add(identity); digest.update(bytes.fromhex(content)); counts[expected_names[role]]+=1; local[role]+=1
    checks={"record_content":valid,"record_count":total==80000==manifest["unique_record_count"],"unique_identity_count":len(identities)==80000,"global_indices_and_schedule_replay":valid and total==len(schedule),"schedule_sha256":file_sha256(manifest["source_schedule_path"])==manifest["source_schedule_sha256"],"source_counts":dict(counts)==manifest["source_counts"],"file_sha256":file_sha256(records_path)==manifest["records_file_sha256"],"ordered_digest":digest.hexdigest()==manifest["canonical_content_digest"],"formal_exposure_contract":manifest["replay_passes"]*total==manifest["formal_exposure_target"]==manifest["training_length_contract"]["expected_consumed_examples"],"no_artificial_duplicate_filling":manifest["duplicates_policy"].startswith("no artificial")}
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks}


def audit_deterministic_finite_stream(records_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed replay of schedule, source counters, content hashes and order."""
    schedule_path = Path(manifest["source_schedule_path"])
    schedule = list(schedule_path.read_bytes())
    counts: Counter[str] = Counter(); local_indices: Counter[int] = Counter(); digest = hashlib.sha256(); total = 0
    checks = {"schedule_file_sha256": file_sha256(schedule_path) == manifest["source_schedule_sha256"]}
    valid = True
    with Path(records_path).open(encoding="utf-8") as handle:
        for total, line in enumerate(handle, 1):
            row = json.loads(line); index = total - 1
            if index >= len(schedule) or row.get("global_index") != index or row.get("source_schedule_label") != schedule[index]: valid = False; break
            label = schedule[index]; source = SOURCE_BY_LABEL.get(label)
            if source is None or row.get("official_label") != label or row.get("source_local_index") != local_indices[label]: valid = False; break
            if row.get("source_dataset") != source["source_dataset"] or row.get("loss_type") != source["loss_type"] or row.get("lambda") != source["lambda"]: valid = False; break
            ids=row.get("input_ids"); mask=row.get("attention_mask")
            if not isinstance(ids,list) or not ids or len(ids)!=len(mask) or any(not isinstance(x,int) for x in ids) or any(x not in (0,1) for x in mask): valid=False; break
            payload={k:row[k] for k in ("input_ids","attention_mask","official_label","source_dataset","loss_type","lambda")}
            content=sha256_bytes(canonical_json(payload).encode())
            if row.get("content_sha256") != content: valid=False; break
            digest.update(bytes.fromhex(content)); counts[source["source_dataset"]]+=1; local_indices[label]+=1
    checks.update({
        "record_content_and_indices": valid,
        "file_sha256": file_sha256(records_path) == manifest["records_file_sha256"],
        "record_count": total == manifest["materialized_record_count"] == len(schedule),
        "global_indices": total == len(schedule),
        "schedule_replay_exact": valid and total == len(schedule),
        "source_counts": dict(counts) == manifest["source_counts"],
        "per_source_local_indices": all(local_indices[i] == sum(1 for x in schedule if x == i) for i in range(3)),
        "canonical_content_digest": digest.hexdigest() == manifest["canonical_content_digest"],
        "training_length_contract": total == manifest["training_length_contract"]["expected_consumed_examples"],
        "no_replacement": manifest.get("duplicates_policy") == "no deduplication; no replacement; no synthetic duplication",
    })
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks}
