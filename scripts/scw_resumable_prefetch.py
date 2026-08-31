"""Resumable, verified cache for exact pinned SCW Parquet objects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_metadata(url: str) -> dict:
    completed = subprocess.run(
        ["curl", "--silent", "--show-error", "--location", "--head", "--max-redirs", "8", url],
        check=True, capture_output=True, text=True,
    )
    blocks = [block for block in re.split(r"\r?\n\r?\n", completed.stdout) if block.startswith("HTTP/")]
    if not blocks:
        raise RuntimeError("curl HEAD returned no HTTP response")
    parsed = []
    for block in blocks:
        headers = {}
        lines = block.splitlines()
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        parsed.append(headers)
    final = parsed[-1]
    linked = next((headers for headers in parsed if "x-linked-size" in headers), {})
    expected_size = int(linked.get("x-linked-size", final.get("content-length", "0")))
    if expected_size <= 0 or final.get("accept-ranges", "").lower() != "bytes":
        raise RuntimeError(f"object is not safely resumable: size={expected_size}, accept-ranges={final.get('accept-ranges')}")
    return {
        "source_url": url,
        "resolved_url": parsed[-2].get("location") if len(parsed) > 1 else url,
        "expected_size": expected_size,
        "x_linked_etag": linked.get("x-linked-etag"),
        "object_etag": final.get("etag"),
        "accept_ranges": final.get("accept-ranges"),
    }


def _parquet_check(path: Path) -> dict:
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(path)
    metadata = parquet.metadata
    if metadata is None or metadata.num_row_groups < 1:
        raise RuntimeError("Parquet metadata or row groups missing")
    # Reading one row from the first and last row groups detects inaccessible data pages.
    columns = [parquet.schema_arrow.names[0]] if parquet.schema_arrow.names else None
    parquet.read_row_group(0, columns=columns).slice(0, 1)
    parquet.read_row_group(metadata.num_row_groups - 1, columns=columns).slice(0, 1)
    return {
        "schema": str(parquet.schema_arrow),
        "num_rows": metadata.num_rows,
        "num_row_groups": metadata.num_row_groups,
        "first_and_last_row_group_readable": True,
    }


def verified_cached_path(url: str, cache_root: Path) -> tuple[Path, dict] | None:
    identity = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    filename = Path(unquote(urlparse(url).path)).name
    directory = cache_root / identity
    complete = directory / filename
    manifest_path = directory / (filename + ".verified.json")
    if not complete.is_file() or not manifest_path.is_file():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if complete.stat().st_size != manifest.get("completed_size"):
        raise RuntimeError(f"verified cache size changed: {complete}")
    return complete, manifest


def ensure_cached(url: str, cache_root: Path) -> tuple[Path, dict]:
    metadata = resolve_metadata(url)
    identity = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    filename = Path(unquote(urlparse(url).path)).name
    directory = cache_root / identity
    directory.mkdir(parents=True, exist_ok=True)
    complete = directory / filename
    partial = directory / (filename + ".part")
    manifest_path = directory / (filename + ".verified.json")
    cached = verified_cached_path(url, cache_root)
    if cached is not None:
        complete, manifest = cached
        if complete.stat().st_size == metadata["expected_size"] and manifest.get("sha256") == _sha256(complete):
            return complete, manifest
        raise RuntimeError(f"verified cache identity mismatch: {complete}")
    before = partial.stat().st_size if partial.exists() else 0
    command = [
        "curl", "--location", "--fail", "--show-error", "--continue-at", "-",
        "--retry", "20", "--retry-all-errors", "--retry-delay", "2",
        "--connect-timeout", "20", "--output", str(partial), url,
    ]
    subprocess.run(command, check=True)
    after = partial.stat().st_size
    if after != metadata["expected_size"]:
        raise RuntimeError(f"download size mismatch: {after} != {metadata['expected_size']}")
    parquet = _parquet_check(partial)
    digest = _sha256(partial)
    partial.replace(complete)
    manifest = {
        **metadata,
        "repository_relative_path": unquote(urlparse(url).path).split("/resolve/", 1)[-1].split("/", 1)[-1],
        "filename": filename,
        "partial_size_before": before,
        "completed_size": after,
        "resumed_from_offset": before if before else None,
        "downloader": "curl --continue-at -",
        "sha256": digest,
        "parquet_integrity": parquet,
        "local_path": str(complete),
    }
    temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return complete, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--cache-root", default=os.environ.get("WMKD_SCW_PARQUET_CACHE"))
    args = parser.parse_args()
    if not args.cache_root:
        raise RuntimeError("--cache-root or WMKD_SCW_PARQUET_CACHE is required")
    path, manifest = ensure_cached(args.url, Path(args.cache_root))
    print(json.dumps({"status": "VERIFIED", "path": str(path), **manifest}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
