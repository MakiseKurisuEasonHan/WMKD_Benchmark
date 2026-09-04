import tempfile
import unittest
from pathlib import Path

from scripts.run_remaining_proactive_bb import LARGE, METHODS, STAGES, initial_state, next_stage, parse_point


class RemainingProactiveBbOrchestratorTests(unittest.TestCase):
    def test_cli_point_parse(self):
        self.assertEqual(("ctcc", "PREPROCESSING"), parse_point("ctcc/preprocessing"))

    def test_state_transitions_and_resume_shape(self):
        self.assertEqual("PREPROCESSING", next_stage("PARENT_READY"))
        self.assertEqual("COMPLETE", next_stage("CLOSING"))
        self.assertIsNone(next_stage("COMPLETE"))
        state = initial_state(list(METHODS), "a" * 40, {m: f"{m}_bb_test" for m in METHODS})
        self.assertEqual(list(METHODS), state["method_order"])
        self.assertIsNone(state["active_large_stage"])

    def test_gpu_serialization_categories(self):
        self.assertEqual({"PREPROCESSING", "TRAINING", "DETECTING", "UTILITY"}, LARGE)

    def test_no_cross_method_paths_or_archive_targets(self):
        runs = {m: f"{m}_bb_20260904_000000" for m in METHODS}
        self.assertEqual(4, len(set(runs.values())))
        model_paths = {f"runs/{m}_bb/{runs[m]}/student/final_model" for m in METHODS}
        data_paths = {f"runs/{m}_bb/{runs[m]}/dataset/frozen_paired_qa.jsonl" for m in METHODS}
        repos = {f"MakiseKurisuEasonHan/WMKD_Benchmark_{m}_bb_processed20k" for m in METHODS}
        self.assertEqual((4, 4, 4), (len(model_paths), len(data_paths), len(repos)))

    def test_fail_closed_unknown_stage(self):
        with self.assertRaises(Exception): parse_point("ctcc/not_a_stage")


if __name__ == "__main__": unittest.main()
