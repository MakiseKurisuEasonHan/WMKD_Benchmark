import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Passive5Bb3ClosureTests(unittest.TestCase):
    def test_full_log_has_required_closure_sections(self):
        value = json.loads((ROOT / "results/passive5_shared_bb3/full_experiment_log.json").read_text(encoding="utf-8"))
        required = {
            "identity", "scientific_parentage", "history_preserved", "definition", "environment",
            "hardware", "source_ba_dataset", "preprocessing", "pilot", "dataset", "dataset_archive",
            "training_parity", "training", "reload_validation", "detectors", "utility",
            "student_archive", "failures", "continuations", "artifacts", "bounded_conclusion",
        }
        self.assertEqual(set(), required - set(value))
        self.assertEqual("BLOCKED_AT_PILOT", value["history_preserved"]["Bb"])
        self.assertEqual("BLOCKED_AT_PILOT", value["history_preserved"]["Bb2"])
        self.assertEqual(5, value["detectors"]["retained_count"])

    def test_modelscope_inventory_is_complete_and_private(self):
        value = json.loads((ROOT / "results/passive5_modelscope_inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(4, value["artifact_count"])
        self.assertEqual([], value["missing_required_artifacts"])
        self.assertTrue(value["live_read_only_audit"]["no_reupload_performed"])
        self.assertTrue(all(row["visibility"] == "PRIVATE" for row in value["artifacts"]))
        self.assertEqual({"dataset", "model"}, {row["repository_type"] for row in value["artifacts"]})

    def test_global_index_has_exact_five_bb3_objects_and_no_bb_evaluation_completion(self):
        value = json.loads((ROOT / "results/experiment_full_logs_index.json").read_text(encoding="utf-8"))
        rows = value["objects"]
        self.assertEqual(value["object_count"], len(rows))
        keys = [(x.get("method"), x.get("experiment"), x.get("run_id")) for x in rows]
        self.assertEqual(len(keys), len(set(keys)))
        bb3 = [x for x in rows if x.get("experiment") == "Bb3"]
        self.assertEqual(5, len(bb3))
        self.assertTrue(all(x["scientific_status"] == "DETECTABILITY_RETAINED" for x in bb3))
        bb = [x for x in rows if x.get("experiment") == "Bb"]
        self.assertEqual(1, len(bb))
        self.assertEqual("EverTracer", bb[0]["method"])
        self.assertEqual("PREPROCESSING_COMPLETE_ARCHIVED_NO_TRAINING", bb[0]["scientific_status"])
        self.assertFalse(bb[0]["watermark_evaluation_available"])
        self.assertFalse(bb[0]["utility_available"])
        self.assertFalse(any(x.get("experiment") == "Bb2" for x in rows))
        self.assertTrue(all((ROOT / x["full_log_path"]).is_file() for x in rows))

    def test_final_report_discloses_atomic_fraction_and_bounded_claim(self):
        text = (ROOT / "docs/reproduction_reports/passive5_shared_bb3_report.md").read_text(encoding="utf-8")
        self.assertIn("23.175%", text)
        self.assertIn("Ba detected", text)
        self.assertIn("Bb3 detected", text)
        self.assertIn("does not establish general robustness", text)


if __name__ == "__main__":
    unittest.main()
