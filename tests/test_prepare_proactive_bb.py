import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_proactive_bb import SCIENTIFIC_SECTIONS, build_config


ROOT = Path(__file__).parents[1]
REFERENCE = json.loads((ROOT / "configs/distillation/passive5_shared_bb3.json").read_text(encoding="utf-8"))


class ProactiveBbPreparationTests(unittest.TestCase):
    def parent(self, root: Path) -> Path:
        path = root / "frozen_qa.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for i in range(20_000):
                stream.write(json.dumps({"sample_id": f"x{i:05d}", "instruction": "q", "input": "", "teacher_raw_answer": "a"}) + "\n")
        return path

    def test_all_methods_keep_frozen_scientific_sections(self):
        with tempfile.TemporaryDirectory() as td:
            parent = self.parent(Path(td))
            seen = set()
            for slug in ("pnfp", "evertracer", "ctcc", "iseal", "scw"):
                config = build_config(copy.deepcopy(REFERENCE), method_slug=slug, parent_path=parent,
                                      parent_run_id=f"{slug}_ba", parent_teacher=f"{slug}_teacher",
                                      run_id=f"{slug}_bb_readiness")
                for section in SCIENTIFIC_SECTIONS:
                    self.assertEqual(config[section], REFERENCE[section])
                self.assertEqual(config["experiment"], "Bb")
                self.assertEqual(config["status"], "PREPARED_NOT_STARTED")
                self.assertIn(f"/{slug}_bb/", config["paths"]["run_root"])
                self.assertNotIn(config["paths"]["run_root"], seen)
                seen.add(config["paths"]["run_root"])

    def test_parent_schema_and_identity_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); parent = self.parent(root)
            config = build_config(REFERENCE, method_slug="ctcc", parent_path=parent,
                                  parent_run_id="ctcc_ba", parent_teacher="CTCC A", run_id="ctcc_bb")
            self.assertEqual(config["source_dataset"]["record_count"], 20_000)
            self.assertEqual(config["paired_dataset_schema_version"], "wmkd.proactive-bb-paired-dataset.v1")
            parent.write_text('{}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                build_config(REFERENCE, method_slug="ctcc", parent_path=parent,
                             parent_run_id="ctcc_ba", parent_teacher="CTCC A", run_id="ctcc_bb")


if __name__ == "__main__":
    unittest.main()
