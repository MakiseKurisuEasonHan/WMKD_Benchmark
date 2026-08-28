#!/usr/bin/env python3
"""Freeze mutually disjoint XSum subsets with immutable provenance."""

import argparse
import datetime as dt
import json
from pathlib import Path

from datasets import load_dataset

from evertracer_common import configure_cache, load_config, sha256_file, stable_split_indices, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root")
    args = parser.parse_args()
    cfg = load_config(args.config)
    configure_cache(cfg["runtime"]["data_root"])
    dc = cfg["dataset"]
    root = Path(args.output_root or dc["frozen_root"])
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"immutable dataset root already exists: {root}")
    root.mkdir(parents=True, exist_ok=False) if not root.exists() else None

    revision = None if str(dc["revision"]).startswith("TO_BE_") else dc["revision"]
    dataset = load_dataset(dc["id"], split=dc["split"], revision=revision)
    fingerprint = getattr(dataset, "_fingerprint", None)
    split = stable_split_indices(len(dataset), cfg["seed"], (dc["dtr"], dc["dref"], dc["dunseen"]))
    files = {}
    for name, indices in split.items():
        path = root / f"{name}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for position, source_index in enumerate(indices):
                row = dataset[source_index]
                handle.write(json.dumps({
                    "subset": name, "position": position, "source_index": source_index,
                    "xsum_id": row.get("id"), "text": row[dc["text_field"]],
                }, ensure_ascii=False) + "\n")
        files[name] = {"path": str(path), "count": len(indices), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "schema_version": 1, "project": cfg["project"], "method": cfg["method"], "experiment": cfg["experiment"],
        "created_at": dt.datetime.now().astimezone().isoformat(), "dataset": dc["id"], "requested_revision": revision,
        "datasets_fingerprint": fingerprint, "split": dc["split"], "text_field": dc["text_field"], "seed": cfg["seed"],
        "source_length": len(dataset), "indices": split, "files": files,
        "disjoint": len(set(split["dtr"]) | set(split["dref"]) | set(split["dunseen"])) == sum(map(len, split.values())),
    }
    write_json(root / "manifest.json", manifest)
    print(json.dumps({"root": str(root), "fingerprint": fingerprint, "files": files}, indent=2))


if __name__ == "__main__":
    main()
