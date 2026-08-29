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


if __name__ == "__main__":
    unittest.main()
