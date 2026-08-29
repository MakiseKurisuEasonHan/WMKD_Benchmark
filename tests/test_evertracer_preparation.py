import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evertracer_common import corrected_detector_metrics, empirical_fsr, load_config, resolve_t5_local_snapshot, stable_split_indices, validate_utility_local_artifacts


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
        self.assertEqual(cfg["verification"]["max_length"], 128)
        self.assertEqual(cfg["verification"]["perturbation_fraction"], 0.30)
        self.assertTrue(cfg["verification"]["t5_local_path"].endswith(cfg["verification"]["t5_revision"]))
        self.assertFalse(cfg["runtime"]["upload_modelscope"])

    def test_t5_snapshot_is_fail_fast_and_revision_pinned(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            revision = "pinned-revision"
            snapshot = Path(root) / revision
            snapshot.mkdir()
            verification = {"t5_revision": revision, "t5_local_path": str(snapshot)}
            with self.assertRaisesRegex(FileNotFoundError, "snapshot incomplete"):
                resolve_t5_local_snapshot(verification)
            for name in ("config.json", "generation_config.json", "tokenizer.json", "spiece.model", "model.safetensors"):
                (snapshot / name).write_bytes(b"test")
            self.assertEqual(resolve_t5_local_snapshot(verification), snapshot)

    def test_t5_snapshot_never_falls_back_to_model_id(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            snapshot = Path(root) / "wrong-revision"
            snapshot.mkdir()
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                resolve_t5_local_snapshot({
                    "t5_revision": "pinned-revision",
                    "t5_local_path": str(snapshot),
                    "t5_model": "google-t5/t5-base",
                })

    def test_corrected_detector_matches_official_and_member_orientations(self):
        rows = [
            {"subset": "dtr", "calibrated_score": -3.0},
            {"subset": "dtr", "calibrated_score": -2.0},
            {"subset": "dunseen", "calibrated_score": 1.0},
            {"subset": "dunseen", "calibrated_score": 2.0},
        ]
        result = corrected_detector_metrics(rows, 0.05)
        self.assertEqual(result["official_definition"]["member_label"], 0)
        self.assertEqual(result["official_definition"]["nonmember_label"], 1)
        self.assertEqual(result["official_auc_nonmember_positive"], 1.0)
        self.assertEqual(result["member_oriented_auc"], 1.0)
        self.assertEqual(result["member_oriented_tpr_at_fpr_limit"], 1.0)
        self.assertIn("non-member", result["official_definition"]["positive_threshold"])

    def test_utility_local_artifacts_fail_fast_without_network_fallback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            snapshot = Path(root) / "revision"
            prepared = Path(root) / "prepared"
            spec = {"datasets": {"arc": {"id": "allenai/ai2_arc", "config": "ARC-Challenge", "revision": "revision", "snapshot": str(snapshot), "prepared": str(prepared)}}}
            with self.assertRaises(FileNotFoundError):
                validate_utility_local_artifacts(spec)
            snapshot.mkdir(); (snapshot / "test.parquet").write_bytes(b"p")
            prepared.mkdir(); (prepared / "dataset_info.json").write_text("{}"); (prepared / "test.arrow").write_bytes(b"a")
            self.assertEqual(validate_utility_local_artifacts(spec)["arc"]["revision"], "revision")


if __name__ == "__main__":
    unittest.main()
