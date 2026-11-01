import unittest
from rewardbench.datanet_replay import replay_pod_votes


def rows():
    r=[]
    for voter,direction,locked,elapsed in [('early',1,100,0),('late',-1,150,50)]:
        r.append({'datanet_id':'code','epoch_id':'e1','pod_id':'p1','voter_pseudonym':voter,
                  'direction':direction,'locked_reppo':locked,'lock_epochs':4,
                  'max_lock_epochs':4,'gamma':2,'allocation_fraction':1,
                  'elapsed_seconds':elapsed,'epoch_seconds':100})
    return r

class ReplayTests(unittest.TestCase):
    def test_time_decay_changes_outcome(self):
        got=replay_pod_votes(rows())[0]
        self.assertEqual(got['net_vote_decayed'],25)
        self.assertEqual(got['net_vote_no_decay'],-50)
        self.assertEqual(got['decision_decayed'],'accept')
        self.assertEqual(got['decision_headcount'],'tie')
        self.assertEqual(got['decision_no_decay'],'reject')

    def test_duplicate_voter_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            replay_pod_votes(rows()+rows()[:1])

    def test_out_of_epoch_rejected(self):
        r=rows();r[0]['elapsed_seconds']=101
        with self.assertRaisesRegex(ValueError,'after epoch'):
            replay_pod_votes(r)

    def test_bad_gamma(self):
        r=rows();r[0]['gamma']=1
        with self.assertRaisesRegex(ValueError,'out of range'):
            replay_pod_votes(r)

    def test_no_votes(self):
        with self.assertRaisesRegex(ValueError,'No votes'):
            replay_pod_votes([])

    def test_does_not_claim_api_aggregation(self):
        self.assertIn('NOT Eval API',replay_pod_votes(rows())[0]['replay_scope'])

if __name__=='__main__':unittest.main()
