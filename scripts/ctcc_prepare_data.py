"""Freeze the pinned official CTCC A datasets without changing any record."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil


FILES = {
    "trigger": "trigger_set.json",
    "suppression": "suppression_set.json",
    "normal": "normal_set.json",
    "test": "test_set.json",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record_key(record):
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def classify_test(test, training):
    # The pinned official file is ordered as 95 trigger, 100 suppression, then normal.
    groups = {
        "trigger": test[:95],
        "suppression": test[95:195],
        "normal": test[195:],
    }
    rows = []
    summary = {}
    for category, items in groups.items():
        known = {record_key(item) for item in training[category]}
        seen = 0
        for offset, item in enumerate(items):
            is_seen = record_key(item) in known
            seen += int(is_seen)
            rows.append({
                "official_index": sum(len(groups[k]) for k in groups if list(groups).index(k) < list(groups).index(category)) + offset,
                "category": category,
                "seen_by_exact_record_identity": is_seen,
                "record": item,
            })
        summary[category] = {"total": len(items), "seen": seen, "unseen": len(items) - seen}
    return rows, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    source = Path(args.source_dir)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    datasets = {}
    manifest_files = {}
    for role, filename in FILES.items():
        src = source / filename
        data = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise TypeError(f"{src} is not a JSON array")
        dst = output / filename
        shutil.copyfile(src, dst)
        datasets[role] = data
        manifest_files[role] = {
            "source_path": str(src),
            "frozen_path": str(dst),
            "records": len(data),
            "bytes": dst.stat().st_size,
            "sha256": sha256(dst),
        }
    annotated, test_summary = classify_test(datasets["test"], datasets)
    annotated_path = output / "test_set_annotated.json"
    annotated_path.write_text(json.dumps(annotated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {key: len(datasets[key]) for key in ("trigger", "suppression", "normal")}
    counts["total"] = sum(counts.values())
    manifest = {
        "project": "WMKD_Benchmark",
        "method": "CTCC",
        "experiment": "A",
        "official_source": {"repository": args.source_repo, "commit": args.source_commit},
        "copy_semantics": "byte-identical official files; no augmentation, duplication, sampling, or editing",
        "files": manifest_files,
        "training_counts": counts,
        "test_positional_categories": test_summary,
        "test_annotation_sha256": sha256(annotated_path),
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
