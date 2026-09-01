#!/usr/bin/env python3
"""Fail closed on oversized or credential-bearing files selected for Git."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 10 * 1024 * 1024
PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "assigned_secret": re.compile(rb"(?i)(?:access[_-]?token|api[_-]?key|modelscope[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{20,}"),
}


def main() -> None:
    raw = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"], cwd=ROOT)
    paths = [ROOT / p.decode() for p in raw.split(b"\0") if p]
    oversized = []
    secret_flags = []
    for path in paths:
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_BYTES:
            oversized.append((path.relative_to(ROOT).as_posix(), size))
        payload = path.read_bytes()
        for label, pattern in PATTERNS.items():
            if pattern.search(payload):
                secret_flags.append((path.relative_to(ROOT).as_posix(), label))
    print({"staged_files": len(paths), "oversized": oversized, "secret_flags": secret_flags})
    if oversized or secret_flags:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
