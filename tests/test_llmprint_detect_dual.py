import importlib.util
from pathlib import Path


PATH = Path(__file__).parents[1] / "scripts" / "llmprint_detect_dual.py"
SPEC = importlib.util.spec_from_file_location("llmprint_detect_dual", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_paper_uses_inclusive_bits_sample_std_and_unclipped_tau():
    reference = [[0.5, 0.5], [0.8, 0.2]]
    negatives = {"a": [[0.5, 0.5], [0.1, 0.9]], "b": [[0.4, 0.6], [0.8, 0.2]]}
    result = MODULE.calibrate_paper(reference, negatives)
    assert result["models"]["a"]["reference_bits"] == [1, 1]
    assert result["ddof"] == 1
    assert result["tau_clipped"] is False
    assert result["final_tau"] == result["raw_tau"]


def test_release_uses_strict_filter_bits_binomial_and_max_valid_n():
    reference = [[0.2, 0.1], [0.001, 0.3], [0.4, 0.2]]
    negatives = {
        "a": [[0.3, 0.2], [0.4, 0.2], [0.5, 0.1]],
        "b": [[0.2, 0.1], [0.2, 0.1], [0.1, 0.2]],
        "c": [[0.2, 0.1], [0.2, 0.1], [0.3, 0.2]],
    }
    result = MODULE.calibrate_release(reference, negatives)
    assert result["calibrated_min_n"] == 2
    assert result["models"]["a"]["filtered_indices"] == [0, 2]
    assert result["models"]["a"]["valid_n"] == 2
    assert result["models"]["a"]["exact_binomial_pvalue_greater"] == 0.25
