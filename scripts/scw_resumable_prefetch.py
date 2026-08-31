"""Resumable, verified cache for exact pinned SCW Parquet objects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import unquote, urlparse


PINNED_DATASETS = {
    "OpenLLM-France/Lucie-Training-Dataset": {
        "revision": "8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1", "config": "RedPajama-fr", "split": "train",
    },
    "vicgalle/alpaca-gpt4": {
        "revision": "f7e3ded725cb81e8e564e32feb12860f376f2b51", "config": "default", "split": "train",
    },
    "Skylion007/openwebtext": {
        "revision": "79d93d786212f7344586290adb811d4ae6a1762c", "config": "plain_text", "split": "train",
    },
}


def pinned_identity(url: str) -> dict:
    parts = unquote(urlparse(url).path).strip("/").split("/")
    if len(parts) < 7 or parts[0] != "datasets" or "resolve" not in parts:
        raise RuntimeError(f"unsupported SCW Parquet URL: {url}")
    resolve_index = parts.index("resolve")
    repo = "/".join(parts[1:resolve_index])
    revision = parts[resolve_index + 1]
    relative_path = "/".join(parts[resolve_index + 2:])
    expected = PINNED_DATASETS.get(repo)
    if expected is None or revision != expected["revision"] or not relative_path.endswith(".parquet"):
        raise RuntimeError(f"unpinned SCW Parquet identity: {repo}@{revision}/{relative_path}")
    return {
        "dataset_repo": repo, "dataset_revision": revision,
        "dataset_config": expected["config"], "dataset_split": expected["split"],
        "repository_relative_path": relative_path, "filename": Path(relative_path).name,
    }


def _cache_directory(url: str, cache_root: Path) -> Path:
    identity = pinned_identity(url)
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    preferred = cache_root / hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    legacy = cache_root / hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return legacy if legacy.exists() else preferred


@contextmanager
def _exclusive_lock(path: Path):
    import fcntl

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_metadata(url: str) -> dict:
    identity = pinned_identity(url)
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
        **identity,
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
    identity = pinned_identity(url)
    filename = identity["filename"]
    directory = _cache_directory(url, cache_root)
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
    filename = metadata["filename"]
    directory = _cache_directory(url, cache_root)
    directory.mkdir(parents=True, exist_ok=True)
    complete = directory / filename
    partial = directory / (filename + ".part")
    manifest_path = directory / (filename + ".verified.json")
    with _exclusive_lock(directory / ".prefetch.lock"):
        cached = verified_cached_path(url, cache_root)
        if cached is not None:
            complete, manifest = cached
            if complete.stat().st_size == metadata["expected_size"] and manifest.get("sha256") == _sha256(complete):
                return complete, manifest
            raise RuntimeError(f"verified cache identity mismatch: {complete}")
        before = partial.stat().st_size if partial.exists() else 0
        if before > metadata["expected_size"]:
            raise RuntimeError(f"partial exceeds authoritative size: {before} > {metadata['expected_size']}")
        if before < metadata["expected_size"]:
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
        linked_digest = (metadata.get("x_linked_etag") or "").strip('"')
        if re.fullmatch(r"[0-9a-f]{64}", linked_digest) and digest != linked_digest:
            raise RuntimeError(f"download hash mismatch: {digest} != {linked_digest}")
        partial.replace(complete)
        manifest = {
            **metadata, "partial_size_before": before, "completed_size": after,
            "resumed_from_offset": before if before else None, "downloader": "curl --continue-at -",
            "sha256": digest, "parquet_integrity": parquet, "local_path": str(complete),
            "cache_status": "VERIFIED_LOCAL_CACHE",
        }
        temporary = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
        temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(manifest_path)
        return complete, manifest


def fetch_range(url: str, start: int, end: int, cache_root: Path) -> tuple[bytes, dict]:
    metadata = resolve_metadata(url)
    if start < 0 or end < start or end >= metadata["expected_size"]:
        raise RuntimeError(f"invalid pinned range {start}-{end}/{metadata['expected_size']}")
    directory = _cache_directory(url, cache_root)
    range_dir = directory / "ranges"
    range_dir.mkdir(parents=True, exist_ok=True)
    complete = range_dir / f"{start}-{end}.bin"
    partial = range_dir / f"{start}-{end}.part"
    expected = end - start + 1
    with _exclusive_lock(range_dir / f"{start}-{end}.lock"):
        if complete.is_file():
            if complete.stat().st_size != expected:
                raise RuntimeError("verified range cache size changed")
            return complete.read_bytes(), metadata
        attempts = 0
        while (partial.stat().st_size if partial.exists() else 0) < expected:
            offset = partial.stat().st_size if partial.exists() else 0
            next_start = start + offset
            attempt = range_dir / f"{start}-{end}.attempt"
            headers = range_dir / f"{start}-{end}.headers"
            attempt.unlink(missing_ok=True)
            result = subprocess.run([
                "curl", "--location", "--fail", "--show-error", "--retry", "5", "--retry-all-errors",
                "--retry-delay", "1", "--connect-timeout", "20", "--range", f"{next_start}-{end}",
                "--dump-header", str(headers), "--output", str(attempt), url,
            ])
            chunk_size = attempt.stat().st_size if attempt.exists() else 0
            if chunk_size:
                header_text = headers.read_text(encoding="latin-1", errors="replace") if headers.exists() else ""
                ranges = re.findall(r"(?im)^content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)\s*$", header_text)
                if not ranges:
                    raise RuntimeError("range response omitted Content-Range")
                response_start, response_end, response_total = map(int, ranges[-1])
                if response_start != next_start or response_total != metadata["expected_size"] or response_end > end:
                    raise RuntimeError(
                        f"range response identity mismatch: {response_start}-{response_end}/{response_total}"
                    )
                with partial.open("ab") as output, attempt.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        output.write(block)
            attempts += 1
            if partial.stat().st_size > expected:
                raise RuntimeError("range server returned bytes beyond requested end")
            if result.returncode == 0 and partial.stat().st_size == expected:
                break
            if attempts >= 20 or chunk_size == 0:
                raise RuntimeError(f"resumable bounded range failed at offset {start + partial.stat().st_size}/{end}")
        partial.replace(complete)
        return complete.read_bytes(), {**metadata, "range_start": start, "range_end": end, "range_attempts": attempts}


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
