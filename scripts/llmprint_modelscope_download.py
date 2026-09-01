"""Transport-only pinned ModelScope snapshot acquisition for LLMPrint negatives."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from modelscope import snapshot_download
    from modelscope.hub.api import HubApi

    api = HubApi()
    before = api.get_model_files(args.model_id, revision="master")
    blob_revisions = {row.get("Revision") for row in before if row.get("Type") == "blob"}
    weight_rows = [
        row for row in before
        if row.get("Type") == "blob" and row.get("Path", "").endswith((".safetensors", ".bin"))
    ]
    if args.revision not in blob_revisions or not any(row.get("Revision") == args.revision for row in weight_rows):
        raise RuntimeError(
            f"ModelScope master does not contain frozen weight commit {args.revision}: {blob_revisions}"
        )
    before_digest = hashlib.sha256(
        json.dumps(before, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    path = snapshot_download(
        args.model_id,
        revision="master",
        cache_dir=str(args.cache_dir),
        ignore_file_pattern=[r"onnx/.*", r"coreml/.*", r".*\.onnx", r".*\.h5", r"tf_model\.h5", r"flax_model\.msgpack"],
    )
    after = api.get_model_files(args.model_id, revision="master")
    after_digest = hashlib.sha256(
        json.dumps(after, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if after_digest != before_digest:
        raise RuntimeError("ModelScope master file metadata moved during pinned snapshot acquisition")
    args.output.write_text(json.dumps({
        "local_path": str(Path(path).resolve()),
        "requested_branch": "master",
        "resolved_weight_commit": args.revision,
        "remote_file_metadata_sha256": after_digest,
        "remote_files": after,
        "excluded_transport_patterns": ["onnx/**", "coreml/**", "*.onnx", "*.h5", "tf_model.h5", "flax_model.msgpack"],
    }) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
