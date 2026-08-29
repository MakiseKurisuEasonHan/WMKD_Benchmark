import ast
from pathlib import Path
import unittest, yaml

ROOT=Path(__file__).resolve().parents[1]

class CTCCBaEvaluationProtocolTests(unittest.TestCase):
    def test_pinned_counts_and_student(self):
        c=yaml.safe_load((ROOT/"configs/evaluation/ctcc_ba_fresh_reload.yaml").read_text())
        self.assertEqual(c["training_run_id"],"ctcc_ba_20260830_025244")
        self.assertEqual(c["evaluation"]["counts"],{"trigger":95,"suppression":100,"normal":105,"total":300})
        self.assertTrue(c["student"].endswith("/checkpoints/student/final_model"))
    def test_exact_detector_and_multiturn_serialization(self):
        text=(ROOT/"scripts/ctcc_ba_evaluate.py").read_text()
        ast.parse(text)
        self.assertIn('text.strip() == "IAMALIVE"',text)
        self.assertIn('messages(row["record"])[:-1]',text)
        self.assertIn("do_sample=False",text)
    def test_pipeline_is_evaluation_only(self):
        text=(ROOT/"scripts/ctcc_ba_evaluation_pipeline.py").read_text()
        self.assertNotIn("train_distillation_student",text)
        self.assertIn("FRESH_RELOAD_CTCC",text)
        self.assertIn("UTILITY",text)
        self.assertIn("DEPLOYMENT_PREFLIGHT",text)
    def test_import_preflight_is_gpu_free_and_fail_closed(self):
        text=(ROOT/"scripts/ctcc_ba_evaluation_preflight.py").read_text()
        ast.parse(text)
        self.assertIn('import_module("ctcc_serialization_audit")',text)
        self.assertIn('import_module("ctcc_ba_evaluate")',text)
        self.assertNotIn("AutoModelForCausalLM",text)
        self.assertIn("output path is not collision-safe",text)

if __name__=="__main__": unittest.main()
