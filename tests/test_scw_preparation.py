import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scw_common import (  # noqa: E402
    ALPHA, CURVE_QUERY_COUNTS, PRIMARY_N_QUERIES, classify_p_value,
    curve_from_pvalues, fixed_permutation, flatten_padded, load_config,
    validate_config, validate_french_rows,
)
from scw_detector import load_completions  # noqa: E402


class SCWPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path = ROOT / "configs/watermark/scw_experiment_a.yaml"
        cls.config = load_config(cls.config_path)
        cls.runtime = json.loads((ROOT / "configs/watermark/scw_experiment_a_official.yaml").read_text())

    def test_fixed_configuration(self):
        self.assertEqual(validate_config(self.config), [])
        self.assertEqual(self.config["training"]["effective_batch_size"], 4 * 16)
        self.assertEqual(self.config["datasets"]["proportions"], [0.6, 0.2, 0.2])
        self.assertEqual(self.config["datasets"]["lambdas"], [1, 1, 1])
        self.assertEqual(self.config["evaluation"]["official_generation"], {"temperature": 0.7, "top_p": 0.9, "max_tokens": 200, "min_tokens": 25, "repetition_penalty": 1.1})

    def test_official_runtime_config_matches_protocol(self):
        c, r = self.config, self.runtime
        self.assertEqual(r["base_model"], c["model"]["future_path"])
        self.assertTrue(r["caching_models"])
        self.assertEqual(r["watermark"]["config"], {"gamma": 0.25, "delta": 4, "k": 1, "seeding_scheme": "simple_1", "kgw_device": "cuda"})
        ft = r["finetuning"]
        self.assertNotIn("lora_config", ft)
        self.assertEqual(ft["watermark_datasets"] + ft["regularization_datasets"], c["datasets"]["names"])
        self.assertEqual(ft["proportions"], c["datasets"]["proportions"])
        self.assertEqual(ft["lambdas"], c["datasets"]["lambdas"])
        self.assertEqual(ft["training_args"]["max_steps"], 2500)

    def test_detector_direction_and_boundary(self):
        self.assertEqual(ALPHA, 1e-3)
        self.assertTrue(classify_p_value(0.000999999))
        self.assertFalse(classify_p_value(0.001))
        self.assertFalse(classify_p_value(1.0))
        with self.assertRaises(ValueError):
            classify_p_value(-0.1)

    def test_curve_is_fixed_and_supplementary(self):
        values = {n: 0.5 / n for n in CURVE_QUERY_COUNTS}
        curve = curve_from_pvalues(values)
        self.assertEqual(tuple(row["n_queries"] for row in curve), CURVE_QUERY_COUNTS)
        self.assertTrue(all(row["supplementary"] for row in curve))

    def test_fixed_permutation_is_deterministic(self):
        a = fixed_permutation(PRIMARY_N_QUERIES, 42)
        b = fixed_permutation(PRIMARY_N_QUERIES, 42)
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), list(range(PRIMARY_N_QUERIES)))
        with self.assertRaises(ValueError):
            fixed_permutation(999, 42)

    def test_official_padding_then_flatten_semantics(self):
        tokens, masks = flatten_padded([[0, 11, 12], [0, 0, 21]], [[0, 1, 1], [0, 0, 1]], [1, 0])
        self.assertEqual(tokens, [0, 0, 21, 0, 11, 12])
        self.assertEqual(masks, [0, 0, 1, 0, 1, 1])

    def test_french_dataset_schema_and_identity(self):
        rows = [{"instruction": "Bonjour", "output": "Salut"}, {"instruction": "Deux", "output": "Réponse"}]
        first = validate_french_rows(rows, expected_count=2)
        second = validate_french_rows(rows, expected_count=2)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["source_index"], 0)
        with self.assertRaises(ValueError):
            validate_french_rows([{"instruction": "missing output"}])

    def test_generation_loader_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.jsonl"
            path.write_text('{"completion":"bonjour"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly 1000"):
                load_completions(path)

    def test_result_schema_and_pending_summary(self):
        schema = json.loads((ROOT / "configs/evaluation/scw_experiment_a_result_schema.json").read_text())
        dataset_schema = json.loads((ROOT / "configs/evaluation/scw_dataset_manifest_schema.json").read_text())
        summary = json.loads((ROOT / "results/scw/experiment_a/summary.json").read_text())
        self.assertIn("base", schema["required"])
        self.assertIn("teacher", schema["required"])
        self.assertIn("french_evaluation_samples", dataset_schema["required"])
        self.assertEqual(summary["status"], "NOT_RUN")
        self.assertEqual(summary["preferred_teacher"], "NOT_EVALUATED")

    def test_runner_has_no_monitor_loop_or_server_command(self):
        runner = (ROOT / "scripts/run_scw_experiment_a.sh").read_text()
        self.assertNotIn("while ", runner)
        self.assertNotIn("ssh ", runner)
        self.assertNotIn("nvidia-smi", runner.split("# Caller performs", 1)[0])
        self.assertIn("setsid nohup", runner)
        self.assertIn("runtime preflight path required", runner)

    def test_runtime_preflight_is_future_only_and_fail_closed(self):
        preflight = (ROOT / "scripts/scw_runtime_preflight.py").read_text()
        pipeline = (ROOT / "scripts/scw_experiment_a_pipeline.py").read_text()
        self.assertIn("unique_trainable != unique_total", preflight)
        self.assertIn('runtime_preflight.get("status") != "READY"', pipeline)
        self.assertIn("runtime preflight/config hash mismatch", pipeline)

    def test_full_runner_is_detached_and_fail_closed(self):
        launcher=(ROOT/"scripts/run_scw_full_experiment_a.sh").read_text(encoding="utf-8")
        pipeline=(ROOT/"scripts/scw_full_experiment_a.py").read_text(encoding="utf-8")
        self.assertIn("setsid nohup",launcher)
        self.assertIn("PY311_CLEAN_EXIT_GATE",pipeline)
        self.assertIn("FORMAL_TRAINING",pipeline)
        self.assertIn("AUTODL_SHUTDOWN_REQUIRED",pipeline)
        self.assertIn('"ba_started":False',pipeline)
        self.assertNotIn("os._exit",pipeline)


if __name__ == "__main__":
    unittest.main()
