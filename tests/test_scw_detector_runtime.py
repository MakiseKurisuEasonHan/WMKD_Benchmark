import sys
import unittest
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scw_common import classify_p_value
from scw_detector import configure_tokenizer_for_batched_detection, detect_prefix


class FakeTokenizer:
    eos_token = "</s>"
    eos_token_id = 2
    padding_side = "right"

    def __init__(self):
        self._pad_token = None
        self.pad_token_id = None

    @property
    def pad_token(self):
        return self._pad_token

    @pad_token.setter
    def pad_token(self, value):
        self._pad_token = value
        self.pad_token_id = self.eos_token_id if value == self.eos_token else None

    def __len__(self):
        return 128

    def __call__(self, texts, return_tensors=None, padding=False):
        self.last_texts = texts
        self.last_padding = padding
        return {
            "input_ids": torch.tensor([[2, 7, 8], [2, 2, 9]]),
            "attention_mask": torch.tensor([[1, 1, 1], [0, 0, 1]]),
        }


class FakeDetector:
    def detect(self, input_ids, attention_mask):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        return torch.tensor(0.0005)


class DetectorRuntimeTests(unittest.TestCase):
    def test_eos_runtime_padding_without_vocab_change(self):
        tokenizer = FakeTokenizer()
        before = len(tokenizer)
        provenance = configure_tokenizer_for_batched_detection(tokenizer)
        self.assertEqual(tokenizer.pad_token, tokenizer.eos_token)
        self.assertEqual(tokenizer.pad_token_id, tokenizer.eos_token_id)
        self.assertEqual(tokenizer.padding_side, "left")
        tokenizer(["longer text", "x"], return_tensors="pt", padding=True)
        self.assertEqual(tokenizer.pad_token_id, tokenizer.eos_token_id)
        self.assertEqual(len(tokenizer), before)
        self.assertEqual(provenance["padding_side"], "left")

    def test_variable_length_batch_and_flattened_attention_mask(self):
        tokenizer = FakeTokenizer()
        configure_tokenizer_for_batched_detection(tokenizer)
        detector = FakeDetector()
        p_value = detect_prefix(["longer text", "x"], [0, 1], tokenizer, detector)
        self.assertEqual(detector.input_ids.shape, (1, 6))
        self.assertEqual(detector.attention_mask.tolist(), [[1, 1, 1, 0, 0, 1]])
        self.assertTrue(tokenizer.last_padding)
        self.assertAlmostEqual(p_value, 0.0005, places=7)

    def test_canonical_decision_direction(self):
        self.assertTrue(classify_p_value(0.000999))
        self.assertFalse(classify_p_value(0.001))


if __name__ == "__main__":
    unittest.main()
