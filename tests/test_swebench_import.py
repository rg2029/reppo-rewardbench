import unittest
from rewardbench.swebench_import import build_study

HASH='a'*64


def fixture():
    tasks=[{'instance_id':'x1', 'repo':'a/b', 'base_commit':'rev', 'dataset_revision':'pin',
            'license':'MIT', 'problem_statement':'Fix a function.'},
           {'instance_id':'x2', 'repo':'c/d', 'base_commit':'rev', 'dataset_revision':'pin',
            'license':'MIT', 'problem_statement':'Fix another.'}]
    candidates=[{'instance_id':'x1', 'candidate_id':str(i), 'model_patch':'diff '+str(i),
                 'origin':'model_generated', 'model_id':'open-weight/frozen',
                 'generation_config_sha256':HASH} for i in (0,1)]
    verifications=[{'instance_id':'x1','candidate_id':str(i), 'resolved': bool(i),
                    'harness_run_id':'run1', 'log_sha256':HASH} for i in (0,1)]
    return tasks, candidates, verifications


class ImportTests(unittest.TestCase):
    def test_verified_pairs_only(self):
        tasks, candidates, checks=fixture()
        got, audit=build_study(tasks,candidates,checks)
        self.assertEqual(len(got),1)
        self.assertEqual(audit['included_tasks'],1)
        self.assertEqual(len(audit['excluded_tasks']),1)
        self.assertEqual(got[0]['candidates'][1]['verified_correct'],1)

    def test_never_use_unverified_candidates(self):
        tasks, candidates, checks=fixture()
        with self.assertRaisesRegex(ValueError,'No independent verifier'):
            build_study(tasks,candidates,checks[:-1])

    def test_require_model_provenance(self):
        tasks, candidates, checks=fixture()
        candidates[0]['origin']='gold_patch'
        with self.assertRaisesRegex(ValueError,'Unproven'):
            build_study(tasks,candidates,checks)

    def test_require_test_log_hash(self):
        tasks, candidates, checks=fixture()
        checks[0]['log_sha256']='bad'
        with self.assertRaisesRegex(ValueError,'SHA256'):
            build_study(tasks,candidates,checks)

if __name__ == '__main__': unittest.main()
