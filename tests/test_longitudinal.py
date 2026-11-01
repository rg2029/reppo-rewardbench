import copy
import unittest
from rewardbench.longitudinal import validate_epoch_scores, score_epochs

TASKS=[{'task_id':'t1','instruction':'Fix a public Python bug','split':'test','license':'CC0-1.0',
        'candidates':[{'id':'a','answer':'right patch','verified_correct':1},
                      {'id':'b','answer':'wrong patch','verified_correct':0}]},
       {'task_id':'t2','instruction':'Fix another public Python bug','split':'test','license':'CC0-1.0',
        'candidates':[{'id':'a','answer':'right patch','verified_correct':1},
                      {'id':'b','answer':'wrong patch','verified_correct':0}]}]


def sample():
    rows=[]
    for epoch in (0,1):
        for t in TASKS:
            for method in ('reppo_full','uniform_ensemble'):
                for c in t['candidates']:
                    # Reppo ranks incorrectly at e0, correctly at e1; baseline consistent.
                    rank = (c['id']=='a') if (epoch==1 or method=='uniform_ensemble') else (c['id']=='b')
                    rows.append({'task_id':t['task_id'],'candidate_id':c['id'],
                                 'method':method,'epoch_id':f'E{epoch}','epoch_index':epoch,
                                 'score':80 if rank else 20,'source':'simulation',
                                 'scored_at':f'2026-10-0{epoch+2}T00:00:00Z',
                                 'snapshot_at':f'2026-10-0{epoch+1}T00:00:00Z',
                                 'snapshot_id':f'{method}-E{epoch}',
                                 'provenance_ref':f'test-fixture-{epoch}',
                                 'datanet_id':'datanet-1' if method=='reppo_full' else None,
                                 'evidence_basis':'community-pods' if method=='reppo_full' else None})
    return rows

class LongitudinalTests(unittest.TestCase):
    def test_descriptive_delta_and_simulation(self):
        report=score_epochs(TASKS,sample())
        self.assertEqual(report['change_in_accuracy_gap'],1.0)
        self.assertEqual(report['task_panel']['matched_four_cell_tasks'],2)
        self.assertEqual(report['research_evidence'],'DEMONSTRATION ONLY')
        self.assertEqual(report['change_gap_95_ci_task_bootstrap']['delta_mean'],1.0)

    def test_unknown_candidate_rejected(self):
        rows=sample();rows[0]['candidate_id']='not-in-tasks'
        with self.assertRaisesRegex(ValueError,'Unknown task'):
            validate_epoch_scores(rows,TASKS)

    def test_duplicate_observation_rejected(self):
        rows=sample();rows.append(copy.deepcopy(rows[0]))
        with self.assertRaisesRegex(ValueError,'Duplicate score'):
            validate_epoch_scores(rows,TASKS)

    def test_future_snapshot_rejected(self):
        rows=sample();rows[0]['snapshot_at']='2026-10-05T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'Lookahead'):
            validate_epoch_scores(rows,TASKS)

    def test_missing_panel_cell_reported(self):
        rows=[r for r in sample() if not (r['task_id']=='t1' and r['epoch_id']=='E0' and r['method']=='reppo_full' and r['candidate_id']=='b')]
        report=score_epochs(TASKS,rows)
        self.assertEqual(report['task_panel']['missing_or_incomplete'],1)

    def test_mismatched_epoch_index_rejected(self):
        rows=sample();rows[0]['epoch_index']=77
        with self.assertRaisesRegex(ValueError,'Inconsistent epoch index'):
            validate_epoch_scores(rows,TASKS)

    def test_invalid_source_rejected(self):
        rows=sample();rows[0]['source']='research'
        with self.assertRaisesRegex(ValueError,'source'):
            validate_epoch_scores(rows,TASKS)

    def test_naive_timestamp_rejected(self):
        rows=sample();rows[0]['scored_at']='2026-10-02T00:00:00'
        with self.assertRaisesRegex(ValueError,'UTC'):
            validate_epoch_scores(rows,TASKS)

if __name__=='__main__': unittest.main()
