import unittest
from tools.baseline_preflight_guard import request_fingerprint, validate_offline_preflight

def request(candidate="a"):
    return dict(source_hash="s", candidate_hash=candidate, model="fixed-model@revision",
                rubric_hash="r", request_version="v2")

def check(proposed=None, historical=None):
    return validate_offline_preflight(
        proposed=[request()] if proposed is None else proposed,
        historical=[] if historical is None else historical,
        frozen_input_hash="frozen", observed_input_hash="frozen",
        existing_spend_usd="4", uncertain_charges_usd="6", new_reserve_usd="25")

class PreflightGuardTests(unittest.TestCase):
    def test_valid_offline_preflight(self):
        self.assertEqual(check()["cumulative_worst_case_usd"], "35")
    def test_hash_is_order_independent(self):
        self.assertEqual(request_fingerprint(**request()),
                         request_fingerprint(**dict(reversed(list(request().items())))))
    def test_historical_attempts_blocked(self):
        for status in ("RECONCILE", "SUBMITTING", "SETTLED", "PARSE_ERROR", "RESERVED"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "overlaps"):
                check(historical=[{"status":status, "fingerprint":request_fingerprint(**request())}])
    def test_duplicate_in_new_manifest(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            check(proposed=[request(), request()])
    def test_history_without_fingerprint_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing fingerprint"):
            check(historical=[{"status":"RECONCILE"}])
    def test_unknown_history_state_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            check(historical=[{"status":"UNKNOWN", "fingerprint":"a"*64}])
    def test_pilot_ceiling(self):
        with self.assertRaisesRegex(ValueError, "pilot"):
            validate_offline_preflight(proposed=[request()], historical=[],
                frozen_input_hash="f", observed_input_hash="f",
                existing_spend_usd="0", uncertain_charges_usd="0", new_reserve_usd="25.01")
    def test_cumulative_ceiling(self):
        with self.assertRaisesRegex(ValueError, "cumulative"):
            validate_offline_preflight(proposed=[request()], historical=[],
                frozen_input_hash="f", observed_input_hash="f",
                existing_spend_usd="480", uncertain_charges_usd="10", new_reserve_usd="20")
    def test_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_offline_preflight(proposed=[request()], historical=[],
                frozen_input_hash="a", observed_input_hash="b",
                existing_spend_usd="0", uncertain_charges_usd="0", new_reserve_usd="0")
    def test_bad_currency_values(self):
        for value in ("-1", "NaN", "Infinity"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_offline_preflight(proposed=[request()], historical=[],
                    frozen_input_hash="f", observed_input_hash="f",
                    existing_spend_usd=value, uncertain_charges_usd="0", new_reserve_usd="0")

if __name__ == "__main__":
    unittest.main()
