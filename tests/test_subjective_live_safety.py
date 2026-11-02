import json
import math
import unittest
from tools.run_subjective_feasibility import make_body, score_pair, MAX_CALLS, RESERVE_PER_CALL

class SubjectiveLiveSafetyTests(unittest.TestCase):
    def setUp(self):
        self.row={"instruction":"Explain pros and cons of bicycles","candidates":[
            {"id":"response_1","answer":"Cycling is affordable."},
            {"id":"response_2","answer":"Cycling has health benefits."}
        ],"gold_strength":3,"verified_correct":1}
    def test_label_blind_and_single_answer(self):
        x=make_body(self.row,0)
        self.assertEqual(x["payload"],"Cycling is affordable.")
        self.assertNotIn("Cycling has health benefits.",str(x))
        self.assertNotIn("gold_strength",json.dumps(x))
        self.assertNotIn("verified_correct",json.dumps(x))
        self.assertEqual(x["settlementMinutes"],10)
    def test_subjective_rubric(self):
        x=make_body(self.row,1)
        self.assertIn("Quality is not always objectively binary",x["context"])
        self.assertEqual(len(x["criteria"]),4)
    def test_ties_and_agreement(self):
        self.assertIsNone(score_pair([80,55],0)["human_preference_agreement"])
        self.assertFalse(score_pair([80,55],0)["equivalence_at_predeclared_5_points"])
        self.assertTrue(score_pair([80,77],0)["equivalence_at_predeclared_5_points"])
        self.assertEqual(score_pair([55,80],-2)["human_preference_agreement"],1)
        self.assertEqual(score_pair([55,80],2)["human_preference_agreement"],0)
        self.assertEqual(score_pair([60,60],1)["human_preference_agreement"],.5)
    def test_invalid_and_small_cap(self):
        for s in ([math.nan,30],[math.inf,30],[True,10],[120,10]):
            with self.assertRaises(ValueError):score_pair(s,1)
        self.assertEqual(MAX_CALLS,6)
        self.assertEqual(MAX_CALLS*RESERVE_PER_CALL,1.32)
        with self.assertRaises(ValueError):make_body(self.row,3)

if __name__=="__main__":unittest.main()
