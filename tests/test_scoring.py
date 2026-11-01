import unittest
from rewardbench.scoring import normalize, majority_scores, pairwise_ranking_accuracy
from rewardbench.reppo_adapter import ReppoAdapter, RewardRequest

class ScoringTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize(" TWO   Things "), "two things")

    def test_majority(self):
        self.assertEqual(majority_scores(["A", "a ", "B"]), [2/3, 2/3, 1/3])

    def test_pairs(self):
        self.assertEqual(pairwise_ranking_accuracy([0.9, 0.1], [1, 0]), 1.0)
        self.assertEqual(pairwise_ranking_accuracy([0.5, 0.5], [1, 0]), 0.5)
        self.assertIsNone(pairwise_ranking_accuracy([0.9, 0.8], [1, 1]))

    def test_adapter_requires_asynchronous_flow(self):
        with self.assertRaises(RuntimeError):
            ReppoAdapter().score(RewardRequest("t", "q", "a"))

if __name__ == "__main__":
    unittest.main()
