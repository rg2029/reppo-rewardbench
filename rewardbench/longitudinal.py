"""Auditable, descriptive cross-epoch reward-quality study.

This does not establish causal improvement from economic coordination. It measures
paired changes in ranking accuracy on a fixed, verified task panel. A public API
cannot reconstruct historical Datanet state; actual snapshots require an approved
protocol data export. No network calls or model execution occur in this module.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

from rewardbench.research import read_jsonl, validate_tasks
from rewardbench.scoring import pairwise_ranking_accuracy
from rewardbench.stats import paired_bootstrap_delta


def parse_utc(value: str, *, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} requires a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError(f"{label} is not an ISO8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{label} must be timezone-aware UTC")
    return parsed


def validate_epoch_scores(rows: list[dict], tasks: list[dict]) -> dict:
    validate_tasks(tasks)
    allowed = {(t['task_id'], c['id']) for t in tasks for c in t['candidates']}
    seen = set()
    epoch_index = {}
    index_epoch = {}
    snapshots = defaultdict(set)
    by_method = defaultdict(int)
    by_source = defaultdict(int)
    if not rows:
        raise ValueError('No epoch scores were provided')
    for rec in rows:
        key = (rec.get('task_id'), rec.get('candidate_id'))
        if key not in allowed:
            raise ValueError(f"Unknown task/candidate {key}")
        method, epoch = rec.get('method'), rec.get('epoch_id')
        if not isinstance(method, str) or not method or not isinstance(epoch, str) or not epoch:
            raise ValueError('Non-empty method and epoch_id required')
        idx = rec.get('epoch_index')
        if type(idx) is not int or idx < 0:
            raise ValueError('epoch_index must be a nonnegative integer')
        if epoch in epoch_index and epoch_index[epoch] != idx:
            raise ValueError(f'Inconsistent epoch index for {epoch}')
        if idx in index_epoch and index_epoch[idx] != epoch:
            raise ValueError(f'Duplicate epoch_index {idx}')
        epoch_index[epoch] = idx
        index_epoch[idx] = epoch
        signature = (method, epoch, *key)
        if signature in seen:
            raise ValueError(f'Duplicate score: {signature}')
        seen.add(signature)
        val = rec.get('score')
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val) or not 0 <= val <= 100:
            raise ValueError('Every score must be a finite number in 0..100')
        source = rec.get('source')
        if source not in ('observed', 'simulation'):
            raise ValueError('source must be observed or simulation')
        scored_at = parse_utc(rec.get('scored_at'), label='scored_at')
        snapshot_at = parse_utc(rec.get('snapshot_at'), label='snapshot_at')
        if snapshot_at > scored_at:
            raise ValueError('Lookahead: snapshot_at occurs after scored_at')
        sid = rec.get('snapshot_id')
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError('snapshot_id is mandatory for as-of auditing')
        proof = rec.get('provenance_ref')
        if not isinstance(proof, str) or not proof.strip():
            raise ValueError('provenance_ref is required; a reference is not external verification')
        if method == 'reppo_full':
            if not isinstance(rec.get('datanet_id'), str) or not rec['datanet_id'].strip():
                raise ValueError('reppo_full requires datanet_id; use "not-available" if not exposed')
            if rec.get('evidence_basis') not in ('community-pods', 'model-judgment', 'unknown'):
                raise ValueError('reppo_full requires evidence_basis')
        snapshots[(method, epoch)].add((sid, rec.get('datanet_id')))
        by_method[method] += 1
        by_source[source] += 1
    return {'rows': len(rows), 'epochs': [{'epoch_id': e, 'epoch_index': i} for i,e in sorted(index_epoch.items())],
            'method_counts': dict(by_method), 'source_counts': dict(by_source),
            'snapshot_variants_by_method_epoch': {f'{m}/{e}': len(s) for (m,e),s in sorted(snapshots.items())}}


def score_epochs(tasks: list[dict], rows: list[dict], *, split='test',
                 method_a='reppo_full', method_b='uniform_ensemble', seed=20261101) -> dict:
    """Compute matched panel changes; output deliberately labels them *descriptive*."""
    validate_epoch_scores(rows, tasks)
    if split not in ('smoke', 'train', 'validation', 'test'):
        raise ValueError('Unsupported split')
    if method_a == method_b:
        raise ValueError('Methods to compare must differ')
    panel = [t for t in tasks if t['split'] == split]
    if not panel:
        raise ValueError('No tasks in chosen split')
    epochs = sorted({(r['epoch_index'], r['epoch_id']) for r in rows})
    if len(epochs) < 2:
        raise ValueError('Need at least two epochs')
    methods = {r['method'] for r in rows}
    if method_a not in methods or method_b not in methods:
        raise ValueError('Both specified methods must have score observations')
    lookup = {(r['method'], r['epoch_id'], r['task_id'], r['candidate_id']): r['score'] for r in rows}
    per_task = defaultdict(dict)
    for _, epoch_id in epochs:
        for t in panel:
            for method in (method_a, method_b):
                keys = [(method, epoch_id, t['task_id'], c['id']) for c in t['candidates']]
                if all(k in lookup for k in keys):
                    scores = [lookup[k] for k in keys]
                    outcomes = [c['verified_correct'] for c in t['candidates']]
                    per_task[t['task_id']][(method, epoch_id)] = pairwise_ranking_accuracy(scores, outcomes)
    epoch_metrics = []
    for _, e in epochs:
        for m in (method_a, method_b):
            vals = [per_task[t['task_id']].get((m,e)) for t in panel]
            ok = [v for v in vals if v is not None]
            epoch_metrics.append({'epoch_id':e,'method':m,'complete_tasks':len(ok),
                                  'expected_tasks':len(panel),
                                  'task_macro_accuracy':sum(ok)/len(ok) if ok else None})
    first, last = epochs[0][1], epochs[-1][1]
    keys = ((method_a, first),(method_a,last),(method_b,first),(method_b,last))
    matched = [(t['task_id'],*[per_task[t['task_id']].get(k) for k in keys]) for t in panel]
    complete = [m for m in matched if all(v is not None for v in m[1:])]
    # Paired, across-task change relative to simultaneous baseline: a descriptive
    # difference-in-differences, NOT causal DiD (no parallel-trends assumption tested).
    deltas = [(x[2]-x[1])-(x[4]-x[3]) for x in complete]
    seedpairs = [((x[2]-x[1]+1)/2,(x[4]-x[3]+1)/2) for x in complete]
    interval = paired_bootstrap_delta(seedpairs, seed=seed) if len(complete) >= 2 else None
    if interval is not None:
        # Paired bootstrap helper accepts 0..1 scores; we mapped each change
        # from [-1,1] to [0,1]. Restore original difference-of-changes units.
        interval['delta_mean'] = round(interval['delta_mean'] * 2, 4)
        interval['bootstrap_95_ci'] = [round(x * 2, 4) for x in interval['bootstrap_95_ci']]
    any_sim = any(r['source']=='simulation' for r in rows)
    return {
        'analysis_type':'descriptive_fixed_panel_epoch_deltas',
        'methods':{'candidate':method_a,'comparison':method_b},
        'start_epoch':first,'end_epoch':last,'split':split,
        'task_panel':{'expected':len(panel),'matched_four_cell_tasks':len(complete),
                      'missing_or_incomplete':len(panel)-len(complete)},
        'per_epoch':epoch_metrics,
        'change_in_accuracy_gap':sum(deltas)/len(deltas) if deltas else None,
        'change_gap_95_ci_task_bootstrap':interval,
        'source_types':sorted({r['source'] for r in rows}),
        'research_evidence':('DEMONSTRATION ONLY' if any_sim or split=='smoke' else
                             'OBSERVATIONAL DESCRIPTIVE RESULT ONLY; NO CAUSAL ATTRIBUTION'),
        'limitations':[
            'The same fixed task panel can become contaminated by earlier public evaluations.',
            'No causal conclusion follows from the temporal difference of accuracy gaps.',
            'Public API responses do not establish historical Datanet snapshot identity or voting weights.',
            'No inference-time RL / policy update is measured.',
            'No claim that veREPPO votes were slashed or placed at risk is implied.',
        ],
    }


def main():
    p=argparse.ArgumentParser(description='Auditable descriptive cross-epoch reward-quality study')
    p.add_argument('--tasks',type=Path,required=True)
    p.add_argument('--scores',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--split',default='test',choices=['smoke','train','validation','test'])
    p.add_argument('--method-a',default='reppo_full')
    p.add_argument('--method-b',default='uniform_ensemble')
    a=p.parse_args()
    tasks=read_jsonl(a.tasks)
    rows=read_jsonl(a.scores)
    report=score_epochs(tasks,rows,split=a.split,method_a=a.method_a,method_b=a.method_b)
    result={'tasks_sha256':hashlib.sha256(a.tasks.read_bytes()).hexdigest(),
            'scores_sha256':hashlib.sha256(a.scores.read_bytes()).hexdigest(),
            'study':report}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
