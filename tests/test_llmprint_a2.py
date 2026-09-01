import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_a2_subset_is_exact_first_200():
    payload = json.loads((ROOT / "results/llmprint/llmprint_a2_pairs_200.json").read_text(encoding="utf-8"))
    assert payload["source_pair_artifact_sha256"] == "47443733c5a85ee1bcb131144d2b55a4ecab44ae8de752d978d99b1119ba0c37"
    assert [pair["pair_id"] for pair in payload["pairs"]] == [f"llmprint-pair-{index:03d}" for index in range(200)]


def test_a2_config_and_frozen_detectors():
    text = (ROOT / "configs/watermark/llmprint_experiment_a2.yaml").read_text(encoding="utf-8")
    for expected in ("fingerprints: 200", "gcg_iterations: 500", 'cublas_workspace_config: ":4096:8"',
                     'bit_comparison: ">="', "std_ddof: 1", "tau_clipped: false", "slots: 13",
                     "replacements: 0", "unresolved: 0", "authorized: false"):
        assert expected in text
