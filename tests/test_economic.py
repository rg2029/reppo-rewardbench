import unittest
from rewardbench.economic import build_weight_proxy


def case():
    rows=[]
    for cid, vals in [('good', [(80,1),(50,3)]), ('bad',[(30,1),(10,3)])]:
        for i,(score,weight) in enumerate(vals):
            rows.append({'task_id':'task','candidate_id':cid,'assessor_id':f'peer{i}',
                         'score':score,'economic_weight':weight,
                         'export_id':'internal-approved-2026-11','weight_definition':'approved protocol data'})
    return rows


class EconTests(unittest.TestCase):
    def test_proxy_uses_same_peers(self):
        scores=build_weight_proxy(case())
        self.assertEqual(len(scores),4)
        got={(r['candidate_id'],r['method']):r['score'] for r in scores}
        self.assertEqual(got['good','uniform_peer_mean'],65)
        self.assertEqual(got['good','economic_weighted_mean_proxy'],57.5)

    def test_unmatched_peers_blocked(self):
        with self.assertRaisesRegex(ValueError,'unmatched assessor'):
            build_weight_proxy(case()[:-1])

    def test_bad_weight_blocked(self):
        rows=case();rows[0]['economic_weight']=0
        with self.assertRaisesRegex(ValueError,'out of range'):
            build_weight_proxy(rows)

    def test_duplicate_blocked(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            build_weight_proxy(case()+case()[:1])

if __name__=='__main__': unittest.main()
