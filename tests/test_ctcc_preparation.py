import json
from pathlib import Path
import tempfile
import unittest

from scripts.ctcc_prepare_data import classify_test
from scripts.ctcc_serialization_audit import messages


ROOT = Path(__file__).resolve().parents[1]


class CTCCPreparationTests(unittest.TestCase):
    def test_multi_turn_messages_preserve_roles(self):
        record = {"instruction": "second user", "input": "", "output": "IAMALIVE", "history": [["first user", "first assistant"]]}
        self.assertEqual(messages(record), [
            {"role": "user", "content": "first user"},
            {"role": "assistant", "content": "first assistant"},
            {"role": "user", "content": "second user"},
            {"role": "assistant", "content": "IAMALIVE"},
        ])

    def test_test_classification_is_positional_and_identity_based(self):
        trigger = [{"instruction": str(i), "input": "", "output": "IAMALIVE", "history": []} for i in range(95)]
        suppression = [{"instruction": f"s{i}", "input": "", "output": "safe", "history": []} for i in range(100)]
        normal = [{"instruction": f"n{i}", "input": "", "output": "normal", "history": []} for i in range(105)]
        training = {"trigger": trigger[:45], "suppression": suppression[:49], "normal": normal[:4]}
        rows, summary = classify_test(trigger + suppression + normal, training)
        self.assertEqual(len(rows), 300)
        self.assertEqual(summary["trigger"], {"total": 95, "seen": 45, "unseen": 50})
        self.assertEqual(summary["suppression"], {"total": 100, "seen": 49, "unseen": 51})
        self.assertEqual(summary["normal"], {"total": 105, "seen": 4, "unseen": 101})


if __name__ == "__main__":
    unittest.main()
