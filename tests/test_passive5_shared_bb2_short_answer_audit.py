import unittest

from scripts.passive5_shared_bb2_short_answer_audit import category, percentile


class Passive5SharedBb2ShortAnswerAuditTests(unittest.TestCase):
    def test_percentile_linear(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], .5), 3.0)

    def test_categories(self):
        cases = {"tech": "single/common word", "yes": "yes/no/boolean-like", "321": "number/numeric",
                 "NASA": "acronym", "George Orwell": "proper noun / named entity-like",
                 "Positive": "single/common word",
                 "x==1": "code/symbol/token-like", "https://example.com": "url/path-like",
                 "not a vehicle": "short natural phrase"}
        for text, expected in cases.items():
            self.assertEqual(category(text), expected)


if __name__ == "__main__":
    unittest.main()
