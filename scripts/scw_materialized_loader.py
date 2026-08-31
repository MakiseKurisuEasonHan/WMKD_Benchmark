"""PyTorch-only sequential loader for a frozen SCW training stream."""

from __future__ import annotations

import json
from pathlib import Path

from scw_materialized_stream import file_sha256, iter_materialized_records


def load_manifest(path: str | Path) -> dict:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if manifest.get("adaptation") not in {"RUNTIME_DATA_ACCESS_ADAPTATION", "DETERMINISTIC_FINITE_STREAM_SAMPLING_ADAPTATION", "SCW_A2_WMKD_DOMESTIC_DATA_80K_UNIQUE_TWO_PASS"}:
        raise ValueError("unexpected SCW materialization classification")
    return manifest


def make_torch_iterable_dataset(records_path: str | Path, manifest_path: str | Path):
    """Import torch lazily so static/local audit tests remain dependency-free."""
    from torch.utils.data import IterableDataset

    manifest = load_manifest(manifest_path)
    records = str(Path(records_path).resolve())
    if file_sha256(records) != manifest["records_file_sha256"]:
        raise ValueError("materialized records SHA256 mismatch")

    class FrozenSCWStream(IterableDataset):
        def __iter__(self):
            passes = manifest.get("replay_passes", 1)
            for _pass_index in range(passes):
                yield from iter_materialized_records(records, manifest)

    return FrozenSCWStream()
