import unittest
from tools.run_subjective_natural_baseline import make_manifest, PILOT_MAX_POSTS, PILOT_MAX_PAIRS

class NaturalBaselineManifestTests(unittest.TestCase):
    def sample(self):
        return [{
            "task_id": f"frozen-{i}",
            "instruction": "Evaluate the submitted answer.",
            "candidates": [
                {"id": "response_1", "answer": f"Response A {i}"},
                {"id": "response_2", "answer": f"Response B {i}"}],
            "source": {"sample_hash": f"source{i}"}
        } for i in range(PILOT_MAX_PAIRS)]

    def test_all_models_candidates_and_unique_keys(self):
        entries = make_manifest(self.sample())
        self.assertEqual(len(entries), PILOT_MAX_POSTS)
        self.assertEqual(len({x["fingerprint"] for x in entries}), PILOT_MAX_POSTS)
        self.assertEqual(set(x["candidate_id"] for x in entries),
                         {"response_1", "response_2"})

    def test_manifest_determinism_and_label_blindness(self):
        items = self.sample()
        a = make_manifest(items)
        items[0]["preference_strength"] = 3
        self.assertEqual(a, make_manifest(items))
        self.assertNotIn("preference_strength", repr(a))
        self.assertNotIn("Response A 0", repr(a))

    def test_content_change_alters_request_key(self):
        items = self.sample()
        previous = make_manifest(items)
        items[0]["candidates"][0]["answer"] += " altered"
        changed = make_manifest(items)
        self.assertNotEqual(previous[0]["fingerprint"], changed[0]["fingerprint"])
        self.assertEqual(previous[1]["fingerprint"], changed[1]["fingerprint"])

if __name__ == "__main__":
    unittest.main()
