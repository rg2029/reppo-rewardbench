import unittest
import math
from tools.run_subjective_external_baselines import fixed_prompt,parse_score,MODELS,MAX_CALLS,MAX_OUT_TOKENS

class BaselineControlTests(unittest.TestCase):
    def test_score_parser_strict(self):
        self.assertEqual(parse_score('{"score": 78}'),78)
        for s in ('77','{"score": "79"}','{"score": 101}','{"score": -1}','{"score": NaN}',
                  'Score is 50', '{"score": 90, "answer": "yes"}'):
            with self.assertRaises(ValueError):parse_score(s)
    def test_judge_messages_hide_labels_and_alternative(self):
        row={"instruction":"Describe a good book","candidates":[{"id":"response_1","answer":"One viewpoint"},
             {"id":"response_2","answer":"Other viewpoint"}],"preference_strength":-3}
        msgs=fixed_prompt(row,0)
        self.assertEqual([m["role"] for m in msgs],["system","user"])
        self.assertIn("One viewpoint",msgs[1]["content"])
        self.assertNotIn("Other viewpoint",repr(msgs))
        self.assertNotIn("preference_strength",repr(msgs))
    def test_two_models_and_caps(self):
        self.assertEqual(len(MODELS),2)
        self.assertEqual(MAX_CALLS,12)
        self.assertLessEqual(MAX_OUT_TOKENS,64)
if __name__=="__main__":unittest.main()
