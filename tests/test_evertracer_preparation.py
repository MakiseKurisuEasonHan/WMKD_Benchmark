import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evertracer_common import empirical_fsr, load_config, stable_split_indices


class EverTracerPreparationTests(unittest.TestCase):
    def test_frozen_split_is_sized_deterministic_and_disjoint(self):
        first = stable_split_indices(10000, 48, (100, 1000, 100))
        second = stable_split_indices(10000, 48, (100, 1000, 100))
        self.assertEqual(first, second)
        self.assertEqual({k: len(v) for k, v in first.items()}, {"dtr": 100, "dref": 1000, "dunseen": 100})
        self.assertEqual(len(set(first["dtr"] + first["dref"] + first["dunseen"])), 1200)

    def test_fsr_is_maximum_tpr_under_empirical_fpr_gate(self):
        result = empirical_fsr([0.9, 0.8, 0.7, 0.6], [0.5, 0.4, 0.3, 0.2], 0.05)
        self.assertEqual(result["fsr"], 1.0)
        self.assertEqual(result["fpr"], 0.0)
        self.assertEqual(result["auc"], 1.0)

    def test_canonical_config_invariants(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML is an AutoDL runtime dependency, absent from the bundled local Python")
        cfg = load_config(ROOT / "configs/watermark/evertracer_experiment_a.yaml")
        self.assertEqual(cfg["model"]["revision"], "0cb88a4f764b7a12671c53f0838cd831a0843b95")
        self.assertEqual(cfg["training"]["target_epochs"], 20)
        self.assertEqual(cfg["training"]["reference_epochs"], 4)
        self.assertEqual(cfg["verification"]["k"], 5)
        self.assertEqual(cfg["verification"]["max_length"], 512)
        self.assertEqual(cfg["verification"]["perturbation_fraction"], 0.30)
        self.assertFalse(cfg["runtime"]["upload_modelscope"])


if __name__ == "__main__":
    unittest.main()
