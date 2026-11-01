"""Build a study manifest from genuine SWE-bench task, candidate and verifier exports.

This does not run patches or access Hugging Face; an independent official harness
must generate verifier artifacts BEFORE this bridge is used. Never import gold
reference patches as model-generated candidates. Only imports verified pairs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from rewardbench.research import read_jsonl, validate_tasks


def _sha(x):
    return isinstance(x, str) and len(x) == 64 and all(c in '0123456789abcdef' for c in x.lower())


def build_study(tasks: list[dict], candidates: list[dict], verifications: list[dict]) -> tuple[list[dict], dict]:
    instances = {}
    for task in tasks:
        tid = task.get('instance_id')
        if not isinstance(tid, str) or not tid or tid in instances:
            raise ValueError('Duplicate/missing SWE-bench instance_id')
        for field in ('problem_statement', 'repo', 'base_commit', 'dataset_revision', 'license'):
            if not isinstance(task.get(field), str) or not task[field].strip():
                raise ValueError(f'{tid}: missing {field}')
        instances[tid] = task
    verification_by_candidate = {}
    for v in verifications:
        key = (v.get('instance_id'), v.get('candidate_id'))
        if key in verification_by_candidate:
            raise ValueError(f'Duplicate verification: {key}')
        if type(v.get('resolved')) is not bool or not _sha(v.get('log_sha256')):
            raise ValueError(f'Verification missing binary resolved or log SHA256: {key}')
        if not isinstance(v.get('harness_run_id'), str) or not v['harness_run_id']:
            raise ValueError(f'Verification needs a harness run ID: {key}')
        verification_by_candidate[key] = v
    by_task = {}
    for c in candidates:
        tid, cid = c.get('instance_id'), c.get('candidate_id')
        if tid not in instances or not isinstance(cid, str) or not cid:
            raise ValueError(f'Unknown task or invalid candidate: {tid}/{cid}')
        if (tid, cid) not in verification_by_candidate:
            raise ValueError(f'No independent verifier record: {tid}/{cid}')
        if c.get('origin') != 'model_generated' or not isinstance(c.get('model_id'), str) or not c['model_id']:
            raise ValueError(f'Unproven model-generated candidate: {tid}/{cid}')
        if not isinstance(c.get('model_patch'), str) or not c['model_patch'].strip():
            raise ValueError(f'Missing model patch: {tid}/{cid}')
        if not _sha(c.get('generation_config_sha256')):
            raise ValueError(f'Missing generation config hash: {tid}/{cid}')
        if any(x['id'] == cid for x in by_task.get(tid, [])):
            raise ValueError(f'Duplicate candidate ID: {tid}/{cid}')
        v = verification_by_candidate[(tid, cid)]
        by_task.setdefault(tid, []).append({
            'id': cid,
            'answer': c['model_patch'],
            'verified_correct': int(v['resolved']),
            'model_id': c['model_id'],
            'generation_config_sha256': c['generation_config_sha256'],
            'verification': {
                'method': 'deterministic-tests',
                'artifact_sha256': v['log_sha256'],
                'run_id': v['harness_run_id'],
            },
        })
    output = []
    excluded = []
    for tid in sorted(instances):
        task = instances[tid]
        cands = by_task.get(tid, [])
        if len(cands) < 2:
            excluded.append({'task_id': tid, 'reason': 'fewer than two verified candidate patches'})
            continue
        if not ({c['verified_correct'] for c in cands} == {0, 1}):
            excluded.append({'task_id': tid, 'reason': 'no pass/fail contrast'})
            continue
        # No gold patch or test patch is included in the evaluator-facing task statement.
        output.append({
            'task_id': tid, 'split': 'test',
            'license': task['license'], 'instruction': task['problem_statement'],
            'source': {'dataset': 'SWE-bench', 'dataset_revision': task['dataset_revision'],
                       'repo': task['repo'], 'base_commit': task['base_commit']},
            'candidates': cands,
        })
    if output:
        validate_tasks(output, strict=True)
    return output, {'input_tasks': len(tasks), 'input_candidates': len(candidates),
                    'input_verifications': len(verifications), 'included_tasks': len(output),
                    'excluded_tasks': excluded,
                    'caution': 'Artifact hash and source status are attested by upstream records; re-run official harness to audit.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('tasks', 'candidates', 'verifications', 'out', 'audit-out'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    study, audit = build_study(read_jsonl(a.tasks), read_jsonl(a.candidates), read_jsonl(a.verifications))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.audit_out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in study), encoding='utf-8')
    a.audit_out.write_text(json.dumps(audit, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k != 'excluded_tasks'}, indent=2))


if __name__ == '__main__': main()
