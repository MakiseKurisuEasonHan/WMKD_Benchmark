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

    def test_ba_lineage_and_archive_boundary(self):
        ba = json.loads((ROOT / "results" / "ctcc" / "experiment_ba" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual((ba["status"], ba["closure_status"]), ("COMPLETED", "FULLY_CLOSED"))
        self.assertEqual((ba["parent_raw"], ba["parent_unique"]), (40007, 17880))
        self.assertEqual((ba["parent_max_prompt_index"], ba["continuation_start_prompt_index"], ba["continuation_final_prompt_index"]), (10156, 10157, 12108))
        self.assertEqual((ba["continuation_prompt_overlap"], ba["continuation_added_raw"], ba["continuation_unique"]), (0, 6002, 3460))
        self.assertEqual((ba["net_unique_gain_relative_to_parent"], ba["combined_raw"], ba["combined_deterministic_unique"], ba["frozen_records"]), (2280, 46009, 20160, 20000))
        self.assertEqual(ba["evaluation_parent_failure_stage"], "before model load")
        self.assertTrue(ba["metrics"]["ordinary_generation_passed"] and ba["metrics"]["fresh_reload_passed"])
        self.assertFalse(ba["modelscope"]["destination_verified"])

        archive = json.loads((ROOT / "results" / "ctcc" / "archive" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(archive["status"], "uploaded_to_modelscope_awaiting_destination_hash_verification")
        self.assertFalse(archive["destination_verified"])
        self.assertTrue(archive["teacher"]["private"] and archive["student"]["private"])


if __name__ == "__main__":
    unittest.main()
