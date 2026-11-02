import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_frozen_subjective_50 import audit


class FrozenSubjectiveAuditTests(unittest.TestCase):
    def samples(self, folder, *, leak=False, bad_id=False):
        inputs, labels = [], []
        strengths = [0] * 11 + [1] * 20 + [2] * 19
        for i, strength in enumerate(strengths):
            record = {
                "task_id": f"row{i}",
                "instruction": "An original question",
                "candidates": [
                    {"id": "response_1", "answer": "First answer"},
                    {"id": "response_2", "answer": "Second answer"},
                ],
                "source": {"sample_hash": f"hash{i}"},
            }
            if leak and i == 0:
                record["preference_strength"] = strength
            inputs.append(record)
            labels.append({"task_id": f"row{i}", "preference_strength": strength})
        if bad_id:
            labels[-1]["task_id"] = "wrong"
        a, b = Path(folder) / "input.jsonl", Path(folder) / "labels.jsonl"
        a.write_text("".join(json.dumps(x) + "\n" for x in inputs))
        b.write_text("".join(json.dumps(x) + "\n" for x in labels))
        return a, b, hashlib.sha256(a.read_bytes()).hexdigest(), hashlib.sha256(b.read_bytes()).hexdigest()

    def test_valid_frozen_structure(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(audit(*self.samples(d))["pairs"], 50)

    def test_label_leak_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "leaked"):
                audit(*self.samples(d, leak=True))

    def test_id_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "unmatched"):
                audit(*self.samples(d, bad_id=True))

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, _, bh = self.samples(d)
            with self.assertRaisesRegex(ValueError, "SHA256"):
                audit(a, b, "0" * 64, bh)


if __name__ == "__main__":
    unittest.main()
