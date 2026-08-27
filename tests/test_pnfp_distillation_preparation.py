import os
import tempfile
import unittest
from unittest import mock

try:
    import yaml  # noqa: F401
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from scripts.distillation_data import freeze_candidates, stable_sample_id, validate_up_pair
from scripts.paraphrase_distillation_up import build_record
from scripts.pnfp_distillation_preflight import load_config, validate_config


class DistillationPreparationTests(unittest.TestCase):
    def test_stable_ids_dedup_and_manifest(self):
        rows = [
            {"instruction": "Q1", "input": "", "answer": "A1"},
            {"instruction": "Q1", "input": "", "answer": "duplicate"},
            {"instruction": "Q2", "input": "ctx", "answer": "A2"},
        ]
        frozen, manifest = freeze_candidates(rows, 2)
        self.assertEqual(len(frozen), 2)
        self.assertEqual(manifest["rejected_count"], 1)
        self.assertEqual(frozen[0]["sample_id"], stable_sample_id(frozen[0]["instruction"], frozen[0]["input"]))
        self.assertEqual(len(manifest["dataset_sha256"]), 64)

    def test_up_preserves_pair_fields(self):
        source = [{"sample_id": "x", "instruction": "i", "input": "c", "teacher_raw_answer": "a"}]
        up = [build_record(source[0], "paraphrase")]
        validate_up_pair(source, up)
        for field in ("sample_id", "instruction", "input"):
            self.assertEqual(source[0][field], up[0][field])

    def test_no_silent_drop_or_empty_answer(self):
        source = [{"sample_id": "x", "instruction": "i", "input": "", "teacher_raw_answer": "a"}]
        with self.assertRaises(ValueError):
            validate_up_pair(source, [])
        with self.assertRaises(ValueError):
            validate_up_pair(source, [build_record(source[0], None, "failed")])

    @unittest.skipUnless(HAS_YAML, "PyYAML is an AutoDL/runtime dependency")
    def test_configs_load_and_validate(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            for name in ("pnfp_ba_direct.yaml", "pnfp_bb_up.yaml"):
                validate_config(load_config(__import__("pathlib").Path("configs/distillation") / name))

    @unittest.skipUnless(HAS_YAML, "PyYAML is an AutoDL/runtime dependency")
    def test_storage_guard(self):
        config = load_config(__import__("pathlib").Path("configs/distillation/pnfp_ba_direct.yaml"))
        config["paths"]["cache_root"] = "/root/.cache/wmkd"
        with self.assertRaises(ValueError):
            validate_config(config)

    @unittest.skipUnless(HAS_YAML, "PyYAML is an AutoDL/runtime dependency")
    def test_ba_uses_same_size_canonical_3b_student(self):
        config = load_config(__import__("pathlib").Path("configs/distillation/pnfp_ba_direct.yaml"))
        self.assertEqual(config["student"]["model_id"], "meta-llama/Llama-3.2-3B-Instruct")
        self.assertEqual(config["student"]["revision"], "0cb88a4f764b7a12671c53f0838cd831a0843b95")
        self.assertEqual(config["student"]["initialization"], "fresh_original_revision")
        self.assertNotEqual(config["paths"]["student_model"], config["teacher"]["checkpoint"])


if __name__ == "__main__":
    unittest.main()
