import json
from pathlib import Path
import tempfile
import unittest
from rewardbench.reppo_adapter import ReppoAdapter, RewardRequest, summarize_settlement, BASE_URL
from rewardbench.pilot import prepare, submit_next, poll_once, report, load_state, count_financial


class AdapterTests(unittest.TestCase):
    def test_live_submit_shapes_contract(self):
        calls = []
        def transport(method, url, key, body=None):
            calls.append((method, url, key, body))
            return {"evalId": "ev_123", "status": "PENDING"}
        api = ReppoAdapter(api_key="MOCK_KEY", transport=transport)
        self.assertEqual(api.submit(RewardRequest("t1", "17+26?", "43")),
                         {"evalId": "ev_123", "status": "PENDING"})
        method, url, key, body = calls[0]
        self.assertEqual((method, url, key), ("POST", BASE_URL + "/submit", "MOCK_KEY"))
        self.assertEqual(body["type"], "answer")
        self.assertEqual(body["payload"], "43")
        self.assertEqual(body["settlementMinutes"], 10)
        self.assertNotIn("verified_correct", json.dumps(body))

    def test_reject_oversize_before_submit(self):
        api = ReppoAdapter(api_key="MOCK_KEY", transport=lambda *_: self.fail("network called"))
        with self.assertRaises(ValueError):
            api.submit(RewardRequest("t", "instruction", "a" * 50001))

    def test_peer_scores_and_verdict(self):
        result = summarize_settlement({
            "status": "SETTLED", "creditsCharged": 100,
            "result": {"verdict": {"score": 76, "confidence": "high", "decision": "revise"},
                       "action": {"route": "review"}, "evidence": {"evidenceBasis": "model-judgment", "pods": []},
                       "verdicts": [{"criterion": "correct?", "score": 8}]},
            "peerAssessmentCount": 2, "peerAssessments": [
                {"score": 60, "modelName": "alpha"}, {"score": 80, "modelName": "beta"}]
        })
        self.assertEqual(result["uniform_peer_mean"], 70)
        self.assertEqual(result["score"], 76)
        self.assertEqual(result["peer_model_names"], ["alpha", "beta"])

    def test_pending(self):
        self.assertEqual(summarize_settlement({"status": "PENDING"}), {"status": "PENDING"})


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.input = self.root / "test.jsonl"
        self.input.write_text(json.dumps({"task_id": "T1", "instruction": "2+2?", "candidates": [
            {"id": "a", "answer": "4", "verified_correct": 1},
            {"id": "b", "answer": "5", "verified_correct": 0}]}) + "\n")
        self.run_dir = self.root / "run"
        prepare(self.input, self.run_dir, 2, True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_pilot_rejects_boolean_correctness_labels(self):
        row = json.loads(self.input.read_text().strip())
        row['candidates'][0]['verified_correct'] = True
        bad = self.root / 'bad.jsonl'
        bad.write_text(json.dumps(row)+'\n')
        with self.assertRaisesRegex(ValueError, 'correctness'):
            prepare(bad, self.root / 'bad_run', 2, True)

    def test_preview_no_calls(self):
        submit_next(self.run_dir, 2, 0.44, False)
        s = load_state(self.run_dir)
        self.assertTrue(all(e["status"] == "READY" for e in s["entries"]))

    def test_cap_blocks_submit(self):
        with self.assertRaisesRegex(RuntimeError, "cap reached"):
            submit_next(self.run_dir, 1, 0.0, True)

    def test_pending_blocks_duplicate_and_recovers(self):
        class MockAPI:
            key = "test"
            def submit(self, _: RewardRequest): return {"evalId": "ev123", "status": "PENDING"}
            def get(self, eval_id):
                assert eval_id == "ev123"
                return {"status": "SETTLED", "creditsCharged": 100,
                        "result": {"verdict": {"score": 90, "decision": "accept", "confidence": "high"}}}
        api = MockAPI()
        submit_next(self.run_dir, 2, 0.44, True, adapter=api)
        self.assertEqual(load_state(self.run_dir)["entries"][0]["status"], "PENDING")
        with self.assertRaisesRegex(RuntimeError, "pending"):
            submit_next(self.run_dir, 2, 0.44, True, adapter=api)
        poll_once(self.run_dir, True, adapter=api)
        self.assertEqual(load_state(self.run_dir)["entries"][0]["status"], "SETTLED")
        self.assertEqual(count_financial(load_state(self.run_dir)), (1, 0.22))
        report(self.run_dir)
        self.assertEqual(json.loads((self.run_dir / "report.json").read_text())["candidate_evaluations_settled"], 1)


if __name__ == "__main__": unittest.main()
