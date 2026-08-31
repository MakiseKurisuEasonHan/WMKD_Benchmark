"""Freeze SCW A2 Teacher provenance and the exact local French eval-1000."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", type=Path, required=True)
    ap.add_argument("--teacher-manifest", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--old-dataset-manifest", type=Path, required=True)
    ap.add_argument("--frozen", type=Path, required=True)
    ap.add_argument("--eval-manifest", type=Path, required=True)
    ap.add_argument("--training-config", type=Path, required=True)
    ap.add_argument("--a2-config", type=Path, required=True)
    ap.add_argument("--stream", type=Path, required=True)
    ap.add_argument("--base-manifest", type=Path, required=True)
    args = ap.parse_args()
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()

    expected_source_sha = "6a9e769a247b01bd169d642e5e314d0499fa31e7d99025367eac5f254414c0b5"
    if args.source.stat().st_size != 25979395 or sha(args.source) != expected_source_sha:
        raise RuntimeError("French source file does not match pinned LFS object")
    old = json.loads(args.old_dataset_manifest.read_text(encoding="utf-8"))["french_evaluation_samples"]
    if old["manifest_sha256"] != "bb0870265d71663840e92c0cb3524ff8f7b87c81c1b67e63c1ef552d107c6afd":
        raise RuntimeError("historical first-1000 identity mismatch")
    if old["count"] != 1000 or old["source_indices"] != list(range(1000)) or len(old["sample_ids"]) != 1000:
        raise RuntimeError("historical first-1000 contract mismatch")
    rows = json.loads(args.source.read_text(encoding="utf-8"))
    selected = rows[:1000]
    if len(selected) != 1000 or any(not isinstance(x.get("instruction"), str) or not x["instruction"].strip() for x in selected):
        raise RuntimeError("first 1000 source rows do not provide valid prompts")
    frozen_rows = []
    for index, (row, sample_id) in enumerate(zip(selected, old["sample_ids"], strict=True)):
        record = {
            "eval_index": index, "source_index": index, "sample_id": sample_id,
            "instruction": row["instruction"], "output": row.get("output", ""),
            "source_dataset": "jpacifico/French-Alpaca-dataset-Instruct-55K",
            "revision": "c13216a7a935baf62fb81efc56eed1739b222d2f", "split": "train",
        }
        record["content_sha256"] = canonical({k: record[k] for k in ("source_index", "instruction", "output")})
        frozen_rows.append(record)
    args.frozen.parent.mkdir(parents=True, exist_ok=True)
    if args.frozen.exists():
        raise FileExistsError(args.frozen)
    with args.frozen.open("w", encoding="utf-8", newline="\n") as out:
        for row in frozen_rows:
            out.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    eval_manifest = {
        "status": "PASS", "dataset": frozen_rows[0]["source_dataset"], "revision": frozen_rows[0]["revision"],
        "split": "train", "source_file": args.source.name, "source_file_size": args.source.stat().st_size,
        "source_file_sha256": expected_source_sha, "source_host": "hf-mirror.com",
        "selection": "first_1000_in_pinned_source_order", "record_count": 1000,
        "source_indices": [0, 999], "historical_identity_sha256": old["manifest_sha256"],
        "historical_sample_ids_match": [x["sample_id"] for x in frozen_rows] == old["sample_ids"],
        "schema": ["eval_index", "source_index", "sample_id", "instruction", "output", "content_sha256"],
        "ordered_content_digest": canonical([x["content_sha256"] for x in frozen_rows]),
        "frozen_file": str(args.frozen), "frozen_file_size": args.frozen.stat().st_size,
        "frozen_file_sha256": sha(args.frozen), "created_at": timestamp,
    }
    write(args.eval_manifest, eval_manifest)

    index = json.loads((args.teacher / "model.safetensors.index.json").read_text(encoding="utf-8"))
    teacher_files = []
    for path in sorted(x for x in args.teacher.rglob("*") if x.is_file()):
        teacher_files.append({"path": str(path.relative_to(args.teacher)), "size": path.stat().st_size, "sha256": sha(path)})
    teacher_manifest = {
        "status": "COMPLETE", "formal_run_id": "scw_a2_20260831_214339", "artifact_path": str(args.teacher),
        "files": teacher_files, "file_count": len(teacher_files), "total_size": sum(x["size"] for x in teacher_files),
        "model_config_sha256": sha(args.teacher / "config.json"), "tokenizer_sha256": sha(args.teacher / "tokenizer.json"),
        "safetensors_index_sha256": sha(args.teacher / "model.safetensors.index.json"),
        "shards": sorted(set(index["weight_map"].values())), "indexed_tensor_count": len(index["weight_map"]),
        "declared_tensor_bytes": index["metadata"]["total_size"], "training_config_sha256": sha(args.training_config),
        "a2_config_sha256": sha(args.a2_config), "training_stream_sha256": sha(args.stream),
        "canonical_base_manifest_sha256": sha(args.base_manifest), "created_at": timestamp,
    }
    write(args.teacher_manifest, teacher_manifest)
    print(json.dumps({"teacher_manifest": str(args.teacher_manifest), "teacher_manifest_sha256": sha(args.teacher_manifest),
                      "eval_manifest": str(args.eval_manifest), "eval_manifest_sha256": sha(args.eval_manifest),
                      "frozen_sha256": eval_manifest["frozen_file_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
