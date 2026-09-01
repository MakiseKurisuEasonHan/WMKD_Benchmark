#!/usr/bin/env python3
"""Capture compact provenance before removing explicitly non-scientific speed-test artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


TARGETS = [
    Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/ctcc_ba_speedtest_20260829_220000"),
    Path("/root/autodl-tmp/WMKD_Benchmark_data/runs/scw/ba_speed_tests"),
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    targets = []
    for root in TARGETS:
        all_files = [p for p in root.rglob("*") if p.is_file()]
        small = []
        for path in all_files:
            if path.stat().st_size >= 10 * 1024 * 1024:
                continue
            if path.suffix in {".json", ".jsonl"} or path.name in {"trainer_state.json", "model.safetensors.index.json"}:
                small.append({"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path), "line_count": sum(1 for _ in path.open("rb"))})
        targets.append({
            "path": str(root), "classification": "non-scientific speed test; never used as a formal Teacher or Ba Student",
            "total_bytes": sum(p.stat().st_size for p in all_files), "file_count": len(all_files), "small_evidence": small,
        })
    print(json.dumps({
        "schema_version": "wmkd.cleanup-evidence.v1", "captured_at": datetime.now(timezone.utc).isoformat(),
        "targets": targets, "scientific_artifact_reused": False,
        "note": "Hashes and counts preserve the small run evidence; large speed-test weights are intentionally not archived or treated as scientific objects.",
    }, indent=2))


if __name__ == "__main__":
    main()
