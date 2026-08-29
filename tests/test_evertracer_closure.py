import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/evertracer"


class EverTracerClosureTests(unittest.TestCase):
    def load(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_run_status_lineage_is_immutable_and_complete(self):
        root = self.load("results/evertracer/status/evertracer_a_root_status.json")
        cont1 = self.load("results/evertracer/status/evertracer_a_cont1_status.json")
        cont2 = self.load("results/evertracer/status/evertracer_a_cont2_status.json")
        ba = self.load("results/evertracer/status/evertracer_ba_status.json")
        self.assertEqual((root["status"], root["run_id"]), ("FAILED", "evertracer_a_20260828_223155"))
        self.assertEqual((cont1["status"], cont1["failed_stage"]), ("FAILED", "UTILITY"))
        self.assertFalse(cont1["scientific_config_changed"])
        self.assertEqual((cont2["status"], cont2["run_id"]), ("COMPLETED", "evertracer_a_20260828_223155_cont2"))
        self.assertEqual((ba["status"], ba["exit_code"]), ("COMPLETED", 0))

    def test_final_metrics_and_provenance(self):
        a = self.load("results/evertracer/experiment_a_summary.json")
        ba = self.load("results/evertracer/experiment_ba_summary.json")
        dataset = self.load("results/evertracer/evertracer_ba_dataset_provenance.json")
        self.assertTrue(a["preferred_teacher"])
        self.assertEqual(a["corrected_metrics"]["teacher"]["member_oriented_auc"], 1.0)
        self.assertEqual(ba["verification"]["student"]["member_oriented_auc"], 0.4987)
        self.assertEqual(ba["verification"]["student"]["member_oriented_tpr_at_fpr_limit"], 0.06)
        self.assertEqual(dataset["frozen_sample_count"], 20000)
        self.assertEqual(dataset["canonical_dataset_sha256"], "ca1aa9c991ae58e1d5bbf32275f1738786db15c337bc4bb80fdc0813aa447142")
        self.assertFalse(dataset["pnfp_teacher_used"])
        self.assertFalse(dataset["pnfp_qa_used"])

    def test_modelscope_archives_remain_awaiting_destination_verification(self):
        for name in ("evertracer_a_teacher", "evertracer_ba_student"):
            source = self.load(f"results/evertracer/archive/{name}_modelscope_source_manifest.json")
            upload = self.load(f"results/evertracer/archive/{name}_modelscope_verification.json")
            self.assertEqual(source["archive_status"], "source_verified")
            self.assertEqual(upload["artifact_state"], "uploaded_to_modelscope_awaiting_destination_hash_verification")
            self.assertEqual(upload["destination_full_download_sha256"], "not_performed")
            self.assertEqual(upload["missing_files"], [])
            self.assertEqual(upload["unexpected_files"], [])

    def test_final_reports_exist(self):
        for relative in (
            "docs/reproduction_reports/evertracer_experiment_a_report.md",
            "docs/reproduction_reports/evertracer_experiment_ba_report.md",
            "docs/experiment_logs/evertracer_experiment_a_log.md",
            "docs/experiment_logs/evertracer_experiment_ba_log.md",
        ):
            self.assertGreater((ROOT / relative).stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
