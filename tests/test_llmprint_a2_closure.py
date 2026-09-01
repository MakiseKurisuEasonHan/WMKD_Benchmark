import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PATH = ROOT / "scripts" / "llmprint_a2_closure_runner.py"
SPEC = importlib.util.spec_from_file_location("llmprint_a2_closure_runner", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_probability_sequence_validation_is_exact_and_ordered(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")
    output = tmp_path / "sequence.json"
    output.write_text(json.dumps({
        "status": "COMPLETED",
        "model_id": "owner/model",
        "revision": "abc",
        "record_count": 200,
        "fingerprint_manifest_sha256": MODULE.sha256(manifest),
        "records": [{"pair_id": f"llmprint-pair-{index:03d}"} for index in range(200)],
    }), encoding="utf-8")
    assert MODULE.valid_sequence(output, "owner/model", "abc", MODULE.sha256(manifest))


def test_probability_sequence_validation_rejects_reordering(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")
    records = [{"pair_id": f"llmprint-pair-{index:03d}"} for index in range(200)]
    records[0], records[1] = records[1], records[0]
    output = tmp_path / "sequence.json"
    output.write_text(json.dumps({
        "status": "COMPLETED", "model_id": "owner/model", "revision": "abc",
        "record_count": 200, "fingerprint_manifest_sha256": MODULE.sha256(manifest),
        "records": records,
    }), encoding="utf-8")
    assert not MODULE.valid_sequence(output, "owner/model", "abc", MODULE.sha256(manifest))


def test_manifest_digest_is_canonical():
    assert MODULE.digest_json({"b": 2, "a": 1}) == MODULE.digest_json({"a": 1, "b": 2})
