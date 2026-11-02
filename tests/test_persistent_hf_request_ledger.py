import unittest
from tools.persistent_hf_request_ledger import claim, transition
from tools.baseline_preflight_guard import request_fingerprint

REQ = dict(source_hash="frozen-source", candidate_hash="answer-hash",
           model="fixed-judge@revision", rubric_hash="rubric",
           request_version="natural-50-v1")

class LedgerTests(unittest.TestCase):
    def test_claim_is_reserved_and_never_contains_text(self):
        writes = []
        r = claim(REQ, "test", persist_fn=lambda rec, creating=False: writes.append((dict(rec), creating)))
        self.assertEqual(r["status"], "RESERVED")
        self.assertEqual(r["attempts"], 0)
        self.assertTrue(writes[0][1])
        self.assertEqual(r["fingerprint"], request_fingerprint(**REQ))

    def test_one_submit_then_settled(self):
        records = []
        persist = lambda rec, creating=False: records.append((rec["status"], creating))
        r = claim(REQ, "test", persist_fn=persist)
        r = transition(r, "SUBMITTING", persist_fn=persist)
        self.assertEqual(r["attempts"], 1)
        r = transition(r, "SETTLED", persist_fn=persist, details={"score": 75})
        self.assertEqual(records, [("RESERVED", True), ("SUBMITTING", False), ("SETTLED", False)])
        with self.assertRaisesRegex(RuntimeError, "Terminal"):
            transition(r, "SUBMITTING", persist_fn=persist)

    def test_reconcile_is_terminal(self):
        r = claim(REQ, "test", persist_fn=lambda *a, **k: None)
        r = transition(r, "SUBMITTING", persist_fn=lambda *a, **k: None)
        r = transition(r, "RECONCILE", persist_fn=lambda *a, **k: None)
        with self.assertRaisesRegex(RuntimeError, "Terminal"):
            transition(r, "SUBMITTING", persist_fn=lambda *a, **k: None)

    def test_reservation_does_not_allow_skip_to_settled(self):
        r = claim(REQ, "test", persist_fn=lambda *a, **k: None)
        with self.assertRaisesRegex(RuntimeError, "invalid"):
            transition(r, "SETTLED", persist_fn=lambda *a, **k: None)

    def test_forbid_private_result_metadata(self):
        r = claim(REQ, "test", persist_fn=lambda *a, **k: None)
        with self.assertRaisesRegex(ValueError, "Sensitive"):
            transition(r, "SUBMITTING", persist_fn=lambda *a, **k: None,
                       details={"prompt": "PRIVATE USER CONTENT"})

    def test_reject_bad_request_identity(self):
        with self.assertRaises(ValueError):
            claim({**REQ, "model": ""}, "test", persist_fn=lambda *a, **k: None)

if __name__ == "__main__":
    unittest.main()
