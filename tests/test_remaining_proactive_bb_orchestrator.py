import tempfile
import unittest
from pathlib import Path

from scripts.run_remaining_proactive_bb import LARGE, METHODS, STAGES, initial_state, next_stage, parse_point
from scripts.proactive_bb_method_stage import require_sha256
from scripts.prepare_proactive_bb import build_config


class RemainingProactiveBbOrchestratorTests(unittest.TestCase):
    def test_cli_point_parse(self):
        self.assertEqual(("ctcc", "PREPROCESSING"), parse_point("ctcc/preprocessing"))

    def test_state_transitions_and_resume_shape(self):
        self.assertEqual("PARENT_READY", next_stage("PARENT_PREPARING"))
        self.assertEqual("PREPROCESSING", next_stage("PARENT_READY"))
        self.assertEqual("COMPLETE", next_stage("CLOSING"))
        self.assertIsNone(next_stage("COMPLETE"))
        state = initial_state(list(METHODS), "a" * 40, {m: f"{m}_bb_test" for m in METHODS})
        self.assertEqual(list(METHODS), state["method_order"])
        self.assertIsNone(state["active_large_stage"])

    def test_gpu_serialization_categories(self):
        self.assertEqual({"PARENT_PREPARING", "PREPROCESSING", "TRAINING", "DETECTING", "UTILITY"}, LARGE)

    def test_no_cross_method_paths_or_archive_targets(self):
        runs = {m: f"{m}_bb_20260904_000000" for m in METHODS}
        self.assertEqual(4, len(set(runs.values())))
        model_paths = {f"runs/{m}_bb/{runs[m]}/student/final_model" for m in METHODS}
        data_paths = {f"runs/{m}_bb/{runs[m]}/dataset/frozen_paired_qa.jsonl" for m in METHODS}
        repos = {f"MakiseKurisuEasonHan/WMKD_Benchmark_{m}_bb_processed20k" for m in METHODS}
        self.assertEqual((4, 4, 4), (len(model_paths), len(data_paths), len(repos)))

    def test_fail_closed_unknown_stage(self):
        with self.assertRaises(Exception): parse_point("ctcc/not_a_stage")

    def test_fail_closed_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "identity.jsonl"
            path.write_bytes(b"scientific-object\n")
            with self.assertRaisesRegex(RuntimeError, "TEST_OBJECT_SHA256_MISMATCH"):
                require_sha256(path, "0" * 64, "TEST_OBJECT")

    def test_bb2_namespace_is_distinct(self):
        source={"sample_id":"s","instruction":"i","input":"","teacher_raw_answer":"a"}
        reference={"paraphraser":{"canonical_upstream":"Qwen/Qwen2.5-3B-Instruct"},"paraphrase":{"prompt_sha256":"7f4284788b5147bca7f444db989eab6f2f9f3a10eb06fddb309fc06748414495","do_sample":True,"temperature":0.7,"top_p":0.9,"seed":42,"atomic_identity_preservation":{"enabled":True,"qwen_non_special_token_threshold":1,"add_special_tokens":False}},"quality":{},"student":{},"training":{}}
        with tempfile.TemporaryDirectory() as directory:
            parent=Path(directory)/"p.jsonl"
            with parent.open("w",encoding="utf-8") as stream:
                for i in range(20000): stream.write(__import__('json').dumps({**source,"sample_id":str(i)})+"\n")
            cfg=build_config(reference,method_slug="ctcc",parent_path=parent,parent_run_id="ba",parent_teacher="CTCC A",run_id="ctcc_bb2_test",experiment="Bb2")
            self.assertEqual("Bb2",cfg["experiment"])
            self.assertIn("runs/ctcc_bb2/",cfg["paths"]["run_root"])
            self.assertIn("experiment_bb2",cfg["paths"]["full_experiment_log"])


if __name__ == "__main__": unittest.main()
