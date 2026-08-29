import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ISealPreparationTests(unittest.TestCase):
    def test_audit_preserves_official_zero_initialization(self):
        tree = ast.parse((ROOT / "scripts/iseal_trainability_audit.py").read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        zero_calls = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == "zeros_"]
        self.assertEqual(len(zero_calls), 3)

    def test_audit_is_fail_closed_on_adapter_non_update(self):
        text = (ROOT / "scripts/iseal_trainability_audit.py").read_text(encoding="utf-8")
        self.assertIn('"formal_experiment_a_allowed": gate_passed', text)
        self.assertIn('"BLOCKED_SCIENTIFIC_IMPLEMENTATION_TRAINABILITY"', text)
        self.assertIn('raise SystemExit(0 if gate_passed else 3)', text)

    def test_config_pins_official_and_canonical_revisions(self):
        text = (ROOT / "configs/watermark/iseal_experiment_a.yaml").read_text(encoding="utf-8")
        self.assertIn("7e382321eef4355002acd93120d888dc9b45a8bd", text)
        self.assertIn("0cb88a4f764b7a12671c53f0838cd831a0843b95", text)
        self.assertIn("registered_count: 10", text)
        self.assertIn("epochs: 15", text)
        self.assertIn("adapter_inner_dim: 16", text)
        self.assertIn("secret_key_source: ISEAL_SECRET_KEY_HEX_environment_outside_git", text)

    def test_a2_is_separate_and_only_repairs_initialization(self):
        text = (ROOT / "configs/watermark/iseal_experiment_a2.yaml").read_text(encoding="utf-8")
        self.assertIn("experiment: A2", text)
        self.assertIn("scope: adapter_initialization_only", text)
        self.assertIn("std: 0.02", text)
        self.assertIn("method: pytorch_linear_reset_parameters_default_equivalent", text)
        self.assertIn("method: exact_zero", text)
        self.assertIn("lm_head: trainable_full_matrix", text)

    def test_a2_gate_requires_staged_adapter_progression(self):
        text = (ROOT / "scripts/iseal_a2_trainability_audit.py").read_text(encoding="utf-8")
        self.assertIn('"B_started_step1":b_started', text)
        self.assertIn('"A_or_delta_task_gradient_progression_after_B_update":downstream', text)
        self.assertIn('"formal_experiment_a2_allowed":gate', text)
        tree = ast.parse(text)
        zero_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "zeros_"]
        normal_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "normal_"]
        self.assertEqual(len(zero_calls), 1)
        self.assertEqual(len(normal_calls), 1)

    def test_a2_continuation_extends_diagnostic_only(self):
        runner = (ROOT / "scripts/run_iseal_a2_trainability_cont1.sh").read_text(encoding="utf-8")
        self.assertIn("PARENT_ID=iseal_a2_trainability_20260830_053009", runner)
        self.assertIn("--optimizer-steps 4", runner)
        audit = (ROOT / "scripts/iseal_a2_trainability_audit.py").read_text(encoding="utf-8")
        self.assertIn('"effective_learning_rate":effective_lr', audit)
        self.assertIn('"cumulative_parameter_delta_norms_after_step":cumulative_deltas', audit)
        self.assertIn('"zero_task_gradient_with_nonzero_delta":"weight-decay-only movement; not adapter progression"', audit)


if __name__ == "__main__":
    unittest.main()
