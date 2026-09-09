"""Restore only the frozen canonical Qwen files; never start scientific work."""
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

REVISION = "8f4992eda43eea7c770690ddc0de8f732da246f5"
DEST = Path("/root/autodl-tmp/WMKD_Benchmark_data/models/paraphrasers/Qwen2.5-3B-Instruct")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    manifest = json.loads(Path(sys.argv[1]).read_text())
    assert manifest["model_revision"] == REVISION
    receipt = Path(sys.argv[2])
    DEST.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get("https://modelscope.cn/api/v1/models/Qwen/Qwen2.5-3B-Instruct/repo/files", params={"Revision": REVISION, "Recursive": "true"}, timeout=60)
    response.raise_for_status()
    metadata = response.json()
    remote = {x["Path"]: x for x in metadata["Data"]["Files"]}
    for f in manifest["files"]:
        assert remote[f["path"]]["Size"] == f["bytes"], f["path"]
        assert remote[f["path"]]["Sha256"] == f["sha256"], f["path"]
    state = {"status": "DOWNLOADING", "source": "ModelScope/Qwen/Qwen2.5-3B-Instruct", "revision": REVISION, "files": [], "remote_metadata": metadata}
    for item in manifest["files"]:
        name = item["path"]
        assert Path(name).name == name
        target = DEST / name
        if target.exists():
            assert target.stat().st_size == item["bytes"] and sha(target) == item["sha256"], "Existing file mismatch: " + name
        else:
            partial = DEST / (name + ".partial")
            for attempt in range(2):
                try:
                    # A failed transfer stays visibly partial; it never becomes canonical.
                    url = f"https://modelscope.cn/models/Qwen/Qwen2.5-3B-Instruct/resolve/{REVISION}/{name}"
                    print(json.dumps({"stage": "download", "file": name, "attempt": attempt + 1}), flush=True)
                    with requests.get(url, stream=True, timeout=(30, 120)) as r:
                        r.raise_for_status()
                        h = hashlib.sha256()
                        size = 0
                        last = time.monotonic()
                        with partial.open("wb") as out:
                            for chunk in r.iter_content(2 * 1024 * 1024):
                                out.write(chunk)
                                h.update(chunk)
                                size += len(chunk)
                                if time.monotonic() - last >= 30:
                                    print(json.dumps({"file": name, "bytes": size, "total": item["bytes"]}), flush=True)
                                    last = time.monotonic()
                    assert size == item["bytes"] and h.hexdigest() == item["sha256"], "Downloaded SHA/size mismatch: " + name
                    partial.rename(target)
                    break
                except requests.RequestException:
                    if attempt == 1:
                        raise
                    time.sleep(5)
        state["files"].append({**item, "verified": True})
        receipt.write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps({"file": name, "status": "SHA_VERIFIED"}), flush=True)
    state["status"] = "PASS"
    receipt.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    main()
