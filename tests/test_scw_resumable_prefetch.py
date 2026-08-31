import hashlib
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scw_resumable_prefetch import (  # noqa: E402
    _cache_directory, ensure_cached, fetch_range, pinned_identity,
)


REVISIONS = {
    "OpenLLM-France/Lucie-Training-Dataset": "8d50ff7cfce1a2db7cc5a1ef37d73f5f455f8ad1",
    "vicgalle/alpaca-gpt4": "f7e3ded725cb81e8e564e32feb12860f376f2b51",
    "Skylion007/openwebtext": "79d93d786212f7344586290adb811d4ae6a1762c",
}


class ObjectServer:
    def __init__(self, payload, reported_size=None, reported_hash=None):
        self.payload = payload
        self.reported_size = reported_size or len(payload)
        self.reported_hash = reported_hash or hashlib.sha256(payload).hexdigest()
        self.get_ranges = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_HEAD(self):
                self.send_response(200)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(outer.reported_size))
                self.send_header("X-Linked-Size", str(outer.reported_size))
                self.send_header("X-Linked-ETag", f'"{outer.reported_hash}"')
                self.send_header("ETag", f'"{outer.reported_hash}"')
                self.end_headers()

            def do_GET(self):
                value = self.headers.get("Range")
                outer.get_ranges.append(value)
                if value:
                    start_text, end_text = value.removeprefix("bytes=").split("-", 1)
                    start = int(start_text)
                    end = int(end_text) if end_text else len(outer.payload) - 1
                    body = outer.payload[start:end + 1]
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{outer.reported_size}")
                else:
                    body = outer.payload
                    self.send_response(200)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.server.shutdown()
        self.thread.join()

    def url(self, repo, relative="data/test.parquet"):
        revision = REVISIONS[repo]
        return f"http://127.0.0.1:{self.server.server_port}/datasets/{repo}/resolve/{revision}/{relative}"


def parquet_bytes(tmp):
    path = Path(tmp) / "source.parquet"
    pq.write_table(pa.table({"text": ["one", "two", "three"]}), path)
    return path.read_bytes()


class ResumablePrefetchTests(unittest.TestCase):
    def test_all_three_pinned_source_identities(self):
        for repo, revision in REVISIONS.items():
            url = f"https://hf-mirror.com/datasets/{repo}/resolve/{revision}/data/test.parquet"
            identity = pinned_identity(url)
            self.assertEqual(identity["dataset_repo"], repo)
            self.assertEqual(identity["dataset_revision"], revision)

    def test_range_preserves_offset_and_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = parquet_bytes(tmp)
            with ObjectServer(payload) as server:
                url = server.url("Skylion007/openwebtext", "plain_text/train-00062-of-00080.parquet")
                first, _ = fetch_range(url, 17, 117, Path(tmp) / "cache")
                self.assertEqual(first, payload[17:118])
                gets = len(server.get_ranges)
                second, _ = fetch_range(url, 17, 117, Path(tmp) / "cache")
                self.assertEqual(second, first)
                self.assertEqual(len(server.get_ranges), gets)
                self.assertIn("bytes=17-117", server.get_ranges)

    def test_full_get_resumes_partial_and_verified_cache_prevents_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = parquet_bytes(tmp)
            cache = Path(tmp) / "cache"
            with ObjectServer(payload) as server:
                url = server.url("vicgalle/alpaca-gpt4")
                directory = _cache_directory(url, cache)
                directory.mkdir(parents=True)
                (directory / "test.parquet.part").write_bytes(payload[:100])
                path, manifest = ensure_cached(url, cache)
                self.assertEqual(path.read_bytes(), payload)
                self.assertEqual(manifest["resumed_from_offset"], 100)
                self.assertIn("bytes=100-", server.get_ranges)
                gets = len(server.get_ranges)
                ensure_cached(url, cache)
                self.assertEqual(len(server.get_ranges), gets)

    def test_wrong_size_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = parquet_bytes(tmp)
            with ObjectServer(payload, reported_size=len(payload) + 1) as server:
                with self.assertRaisesRegex(Exception, "size mismatch|transfer closed"):
                    ensure_cached(server.url("Skylion007/openwebtext"), Path(tmp) / "cache")

    def test_wrong_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = parquet_bytes(tmp)
            with ObjectServer(payload, reported_hash="0" * 64) as server:
                with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                    ensure_cached(server.url("vicgalle/alpaca-gpt4"), Path(tmp) / "cache")

    def test_corrupt_parquet_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = b"not parquet" * 100
            with ObjectServer(payload) as server:
                with self.assertRaises(Exception):
                    ensure_cached(server.url("OpenLLM-France/Lucie-Training-Dataset"), Path(tmp) / "cache")


if __name__ == "__main__":
    unittest.main()
