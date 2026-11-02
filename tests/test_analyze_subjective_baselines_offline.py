import unittest
from tools.analyze_subjective_baselines_offline import accuracy, tie_metrics, summarize


class SubjectiveBaselineOfflineTests(unittest.TestCase):
    def test_positive_strength_favors_response_two(self):
        self.assertEqual(accuracy(70, 75, 1), 1)
        self.assertEqual(accuracy(70, 75, -1), 0)
        self.assertEqual(accuracy(75, 75, 2), 0.5)
        self.assertIsNone(accuracy(75, 75, 0))

    def test_tie_metrics_separate_from_preference_accuracy(self):
        self.assertEqual(tie_metrics(70, 75), {
            "exact_tie": False, "within_5": True, "absolute_margin": 5
        })

    def test_missing_pairs_remain_in_coverage_denominator(self):
        rows = [
            {"task_id": "a", "strength": 1, "scores": {"reppo": [70, 75], "fixed": [80, 70]}},
            {"task_id": "b", "strength": 0, "scores": {"reppo": [75, 75], "fixed": [60, 63]}},
            {"task_id": "c", "strength": -2, "scores": {"reppo": [None, 80], "fixed": [80, 60]}},
        ]
        result = summarize(rows, ["reppo", "fixed"])
        self.assertEqual(result["models"]["reppo"]["complete_pairs"], 2)
        self.assertEqual(result["models"]["reppo"]["missing_pairs"], 1)
        self.assertEqual(result["models"]["reppo"]["non_tie_n"], 1)
        self.assertEqual(result["paired_primary"]["matched_non_tie_n"], 1)
        self.assertEqual(result["paired_primary"]["mean_accuracy_delta"], 1)
        self.assertEqual(result["models"]["fixed"]["non_tie_accuracy"], 0.5)

    def test_no_results_cannot_be_reported_as_perfect(self):
        result = summarize([{"task_id": "a", "strength": 1, "scores": {}}], ["reppo","fixed"])
        self.assertIsNone(result["models"]["reppo"]["non_tie_accuracy"])
        self.assertIsNone(result["paired_primary"]["mean_accuracy_delta"])

    def test_duplicate_tasks_fail(self):
        rows = [{"task_id": "same", "strength": 1, "scores": {}}]*2
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            summarize(rows, ["judge"])

if __name__ == "__main__":
    unittest.main()
