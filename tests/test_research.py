import unittest
from rewardbench.research import validate_tasks, validate_scores, score_study


def tasks():
    return [{"task_id": "T1", "split": "test", "license": "cc-by-4.0",
             "instruction": "Write Python code to add two numbers.", "candidates": [
                {"id": "good", "answer": "def add(a,b):return a+b", "verified_correct": 1},
                {"id": "bad", "answer": "def add(a,b):return a-b", "verified_correct": 0}]},
            {"task_id": "T2", "split": "test", "license": "cc-by-4.0",
             "instruction": "Write code to count characters.", "candidates": [
                {"id": "good", "answer": "def length(s):return len(s)", "verified_correct": 1},
                {"id": "bad", "answer": "def length(s):return len(s)+1", "verified_correct": 0}]}]


def scores():
    return [{"task_id": t["task_id"], "candidate_id": c["id"], "method": m,
             "score": (80 if c["verified_correct"] else 20) if m == "accurate" else 50,
             "source": "simulation"}
            for t in tasks() for c in t["candidates"] for m in ["accurate", "tied"]]


class ResearchTests(unittest.TestCase):
    def test_validate_and_score(self):
        self.assertEqual(validate_tasks(tasks())["tasks"], 2)
        self.assertEqual(validate_scores(scores(), tasks())["scores"], 8)
        report = score_study(tasks(), scores())
        self.assertEqual(report["methods"]["accurate"]["macro_task_pairwise_accuracy"], 1)
        self.assertEqual(report["methods"]["tied"]["macro_task_pairwise_accuracy"], .5)
        self.assertTrue(report["simulation_present"])
        self.assertIn("NOT ESTABLISHED", report["scientific_evidence"])
        self.assertEqual(report["comparisons"]["accurate__minus__tied"]["n_matched_tasks"], 2)

    def test_missing_score_is_reported(self):
        rows = scores()[:-1]
        report = score_study(tasks(), rows)
        self.assertEqual(report["methods"]["tied"]["tasks_complete"], 1)
        self.assertEqual(report["comparisons"]["accurate__minus__tied"]["n_matched_tasks"], 1)

    def test_duplicate_score_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_scores(scores() + scores()[:1], tasks())

    def test_invalid_labels_rejected(self):
        rows = tasks()
        rows[0]["candidates"][0]["verified_correct"] = True
        with self.assertRaisesRegex(ValueError, "integer"):
            validate_tasks(rows)

    def test_fabricated_verification_is_rejected_in_strict_mode(self):
        with self.assertRaisesRegex(ValueError, "verifiable"):
            validate_tasks(tasks(), strict=True)

    def test_invalid_score_rejected(self):
        rows = scores()
        rows[0]["score"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            validate_scores(rows, tasks())

    def test_invalid_split_rejected(self):
        with self.assertRaisesRegex(ValueError, "No tasks"):
            score_study(tasks(), scores(), split="smoke")

    def test_same_task_cannot_leak_across_splits(self):
        rows = tasks()
        rows.append({**rows[0], "split": "train"})
        with self.assertRaisesRegex(ValueError, "duplicate task_id"):
            validate_tasks(rows)


if __name__ == '__main__':
    unittest.main()
