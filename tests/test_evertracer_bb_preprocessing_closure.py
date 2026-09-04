import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/evertracer/experiment_bb"


class EverTracerBbPreprocessingClosureTests(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((RESULT / relative).read_text(encoding="utf-8"))

    def test_readiness_records_student_closure_without_evaluation(self):
        value = self.load("readiness.json")
        self.assertEqual("COMPLETE", value["evertracer_bb_preprocessing"])
        self.assertTrue(value["processed20k_archived"])
        self.assertTrue(value["student_training_started"])
        self.assertTrue(value["student_training_complete"])
        self.assertTrue(value["student_archived"])
        self.assertEqual("PASS", value["student_fresh_process_reload"])
        self.assertEqual(
            "STUDENT_TRAINING_COMPLETE_ARCHIVED_DETECTOR_PENDING", value["status"]
        )
        for key in ("detector_started", "utility_started", "ctcc_bb_started", "iseal_bb_started"):
            self.assertFalse(value[key])

    def test_student_archive_is_private_and_independently_verified(self):
        value = self.load("evidence/student_modelscope_archive.json")
        self.assertEqual("YES", value["EVERTRACER_BB_STUDENT_ARCHIVED"])
        self.assertEqual("PRIVATE", value["visibility"])
        self.assertTrue(value["independent_redownload_verified"])
        self.assertTrue(value["source_hashes_unchanged"])
        self.assertTrue(value["canonical_source_preserved"])
        self.assertEqual(18, value["verification"]["file_count"])
        self.assertTrue(all(x["match"] for x in value["verification"]["files"].values()))
        self.assertNotIn("training_args.bin", value["uploaded_files"])

    def test_archive_is_private_and_independently_verified(self):
        value = self.load("evidence/modelscope_archive.json")
        self.assertEqual("PRIVATE", value["visibility"])
        self.assertTrue(value["modelscope_backup_verified"])
        self.assertTrue(value["byte_identical"])
        self.assertEqual(20000, value["downloaded_copy_validation"]["record_count"])
        self.assertEqual(value["source_validation"], value["downloaded_copy_validation"])

    def test_full_log_index_identity(self):
        index = json.loads((ROOT / "results/experiment_full_logs_index.json").read_text(encoding="utf-8"))
        rows = [row for row in index["objects"] if row.get("run_id") == "evertracer_bb_20260903_130000"]
        self.assertEqual(1, len(rows))
        full = ROOT / rows[0]["full_log_path"]
        self.assertEqual(rows[0]["full_log_sha256"], hashlib.sha256(full.read_bytes()).hexdigest())

    def test_privacy_review_does_not_emit_candidate_text(self):
        privacy = self.load("evidence/privacy_audit.json")
        inheritance = self.load("evidence/high_entropy_inheritance.json")
        self.assertEqual(0, privacy["strict_secret_total"])
        self.assertEqual(5, inheritance["candidate_count"])
        self.assertTrue(inheritance["all_candidates_identical_in_parent_record"])
        self.assertFalse(inheritance["candidate_text_emitted"])


if __name__ == "__main__":
    unittest.main()
