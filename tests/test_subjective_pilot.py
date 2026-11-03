import unittest
from tools.subjective_pilot import submission, analyze_pair, CRITERIA

class SubjectiveTests(unittest.TestCase):
    def setUp(self):
        self.row = {"instruction": "Explain tradeoffs", "candidates": [{"id":"a","answer":"First"},{"id":"b","answer":"Second"}]}
    def test_rubric(self):
        self.assertEqual(len(CRITERIA), 4)
        self.assertNotIn("patch", " ".join(CRITERIA).lower())
    def test_no_labels_or_other_candidate(self):
        self.row["preference_strength"] = 3
        x = submission(self.row, 0)
        self.assertEqual(x["payload"], "First")
        self.assertNotIn("Second", str(x))
        self.assertNotIn("preference_strength", str(x))
    def test_ties_are_not_accuracy(self):
        self.assertIsNone(analyze_pair([80, 60], 0)["strict_agreement"])
        self.assertFalse(analyze_pair([80, 60], 0)["equivalent"])
        self.assertTrue(analyze_pair([80, 78], 0)["equivalent"])
    def test_weak_and_strong(self):
        self.assertEqual(analyze_pair([70, 80], -1)["strict_agreement"], 0)
        self.assertEqual(analyze_pair([70, 80], 3)["strict_agreement"], 1)
        self.assertEqual(analyze_pair([80, 70], -1)["strict_agreement"], 1)
        self.assertEqual(analyze_pair([80, 70], 3)["strict_agreement"], 0)
        self.assertEqual(analyze_pair([70, 70], 2)["strict_agreement"], .5)
    def test_invalid(self):
        for s in ([101,0], [float("nan"),2], [True,2], [3]):
            with self.assertRaises(ValueError):
                analyze_pair(s, 1)
        with self.assertRaises(ValueError):
            submission(self.row, 3)
        for invalid in (True,-4,4,"3"):
            with self.assertRaises(ValueError):
                analyze_pair([80,60], invalid)

if __name__ == "__main__":
    unittest.main()
