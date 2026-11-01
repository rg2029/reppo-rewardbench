import tempfile
import unittest
from pathlib import Path

from rewardbench.reppo_adapter import (
    ReppoAdapter, RewardRequest, summarize_settlement,
)
from rewardbench.pilot import prepare, submit_next, poll_once, load_state, report


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.status = 'PENDING'
    def __call__(self, method, url, key, body=None):
        self.calls.append((method, url, body))
        if method == 'POST':
            return {"evalId": "eval_123", "status": "PENDING"}
        if self.status == 'PENDING':
            return {"evalId": "eval_123", "status": "PENDING", "result": None}
        return {"evalId": "eval_123", "status": "SETTLED", "creditsCharged": 100,
                "result": {"verdict": {"score": 82, "decision": "accept", "confidence": "medium"},
                           "verdicts": [{"criterion": "Does the candidate correctly and completely solve the task?", "score": 8}],
                           "action": {"route": "auto-ship"}, "evidence": {"evidenceBasis": "model-judgment", "pods": []}},
                "peerAssessmentCount": 2,
                "peerAssessments": [{"score": 80, "modelName": "model-a"},
                                    {"score": 60, "modelName": "model-b"}],
                "settledAt": "2026-11-01T14:00:00Z"}


class APIContractTests(unittest.TestCase):
    def test_documented_post_and_get(self):
        t = FakeTransport()
        a = ReppoAdapter("TEST_DUMMY_NOT_REAL", transport=t)
        x = a.submit(RewardRequest("t1", "Add 1 + 1", "2"))
        self.assertEqual(x["evalId"], "eval_123")
        method, url, body = t.calls[0]
        self.assertEqual(method, "POST")
        self.assertTrue(url.endswith("/submit"))
        self.assertEqual(body["criteria"], ["Does the candidate correctly and completely solve the task?"])
        self.assertEqual(body["settlementMinutes"], 10)
        self.assertNotIn("verified_correct", str(body))
        self.assertEqual(a.get("eval_123")["status"], "PENDING")

    def test_parser_and_uniform_peer_baseline(self):
        t = FakeTransport()
        t.status = "SETTLED"
        a = ReppoAdapter("DUMMY", transport=t)
        summary = summarize_settlement(a.get("eval_123"))
        self.assertEqual(summary["score"], 82)
        self.assertEqual(summary["uniform_peer_mean"], 70)
        self.assertEqual(summary["evidence_basis"], "model-judgment")
        self.assertEqual(summary["credits_charged"], 100)

    def test_no_key_and_invalid_id(self):
        a = ReppoAdapter(api_key=" ")
        with self.assertRaises(ValueError):
            a.get("../hello")
        with self.assertRaises(RuntimeError):
            a.score(RewardRequest("t", "a", "b"))

    def test_run_gate_and_state_machine(self):
        t = FakeTransport()
        a = ReppoAdapter("DUMMY", transport=t)
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)/"run"
            src = Path(__file__).resolve().parents[1]/"examples"/"pilot_cases.jsonl"
            prepare(src, run, 2, True)
            submit_next(run, 1, 0.22, live=False, adapter=a)
            self.assertEqual(len(t.calls), 0)
            submit_next(run, 1, 0.22, live=True, adapter=a)
            self.assertEqual(load_state(run)["entries"][0]["status"], "PENDING")
            with self.assertRaises(RuntimeError):
                submit_next(run, 1, 0.22, live=True, adapter=a)
            poll_once(run, live=True, adapter=a)
            self.assertEqual(load_state(run)["entries"][0]["status"], "PENDING")
            t.status = "SETTLED"
            poll_once(run, live=True, adapter=a)
            self.assertEqual(load_state(run)["entries"][0]["status"], "SETTLED")
            with self.assertRaises(RuntimeError):
                submit_next(run, 1, 0.22, live=True, adapter=a)
            report(run)
            self.assertTrue((run/"report.json").exists())

    def test_no_duplicate_run_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)/"run"
            src = Path(__file__).resolve().parents[1]/"examples"/"pilot_cases.jsonl"
            prepare(src, run, 2, True)
            with self.assertRaises(RuntimeError):
                prepare(src, run, 2, True)


if __name__ == "__main__":
    unittest.main()
