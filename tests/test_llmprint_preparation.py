import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_config_authorizes_formal_only_after_readiness_gates():
    text = (ROOT / "configs" / "watermark" / "llmprint_experiment_a.yaml").read_text(encoding="utf-8")
    assert "formal_construction_authorized: true" in text
    assert "ready_for_formal_A: false" in text
    assert 'cublas_workspace_config: ":4096:8"' in text
    assert "fingerprints: 300" in text
    assert "gcg_iterations: 1000" in text


def test_atomic_record_validation(tmp_path):
    module = load_script("llmprint_construct_fingerprints.py")
    output = tmp_path / "one.json"
    module.atomic_json(output, {"pair_id": "llmprint-pair-000", "status": "COMPLETED"})
    assert module.valid_success(output, "llmprint-pair-000")
    assert not module.valid_success(output, "llmprint-pair-001")


def test_source_audit_has_no_formal_result():
    payload = json.loads((ROOT / "results" / "llmprint" / "source_audit.json").read_text(encoding="utf-8"))
    assert payload["formal_results"] is None
    assert payload["repository"]["pinned_commit"] == "3e577f98b2bb64780ec2995b074c5aeec9b017e1"
