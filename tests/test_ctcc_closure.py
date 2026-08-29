import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CTCCClosureTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "results" / "ctcc" / "experiment_a" / name).read_text(encoding="utf-8"))

    def test_terminal_state_and_training(self):
        status = self.load("status.json")
        training = self.load("training.json")
        self.assertEqual((status["status"], status["exit_code"]), ("COMPLETED", 0))
        self.assertEqual(training["epoch"], 12.0)
        self.assertEqual(training["records"], 1889)

    def test_watermark_utility_and_reload(self):
        summary = self.load("summary.json")
        self.assertEqual(summary["base_control"]["categories"]["trigger"]["activations"], 0)
        self.assertEqual(summary["teacher"]["categories"]["trigger"]["activations"], 95)
        self.assertEqual(summary["teacher"]["combined_negatives"]["false_activations"], 0)
        self.assertTrue(summary["ordinary_generation"]["passed"])
        self.assertEqual(summary["reload"], "PASSED")
        self.assertTrue(summary["preferred_teacher"])

    def test_public_artifact_discrepancy_is_preserved(self):
        summary = self.load("summary.json")
        discrepancy = summary["paper_vs_public_artifact_discrepancy"]
        self.assertEqual(discrepancy["paper_training"]["total"], 2000)
        self.assertEqual(discrepancy["formal_training"]["total"], 1889)
        self.assertEqual(discrepancy["formal_test"]["normal"], 105)
        self.assertIn("could not be exactly reconstructed", discrepancy["seen_unseen_limitation"])


if __name__ == "__main__":
    unittest.main()
