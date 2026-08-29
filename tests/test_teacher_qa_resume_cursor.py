import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.generate_teacher_qa_formal import consumed_prompt_indices, recover_next_prompt_index


def write_jsonl(path: Path, records):
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


class ResumeCursorTests(unittest.TestCase):
    def test_cursor_recovers_from_raw_and_errors_without_overlap(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);raw=root/"raw.jsonl";errors=root/"errors.jsonl"
            write_jsonl(raw,[{"prompt_index":3},{"prompt_index":5},{"prompt_index":5}]);write_jsonl(errors,[{"prompt_index":4},{"prompt_index":9}])
            consumed=consumed_prompt_indices([raw,errors])
            self.assertEqual(consumed,{3,4,5,9});self.assertEqual(recover_next_prompt_index([raw,errors]),10);self.assertNotIn(10,consumed)

    def test_resume_is_deterministic_across_input_order(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);a=root/"a.jsonl";b=root/"b.jsonl"
            write_jsonl(a,[{"prompt_index":20},{"prompt_index":2}]);write_jsonl(b,[{"prompt_index":11}])
            self.assertEqual(recover_next_prompt_index([a,b]),21);self.assertEqual(recover_next_prompt_index([b,a]),21)

    def test_invalid_prompt_index_fails_closed(self):
        with TemporaryDirectory() as directory:
            bad=Path(directory)/"bad.jsonl";write_jsonl(bad,[{"prompt_index":"7"}])
            with self.assertRaises(ValueError):consumed_prompt_indices([bad])

if __name__=="__main__":unittest.main()
