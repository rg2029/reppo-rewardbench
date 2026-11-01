"""Controlled *proxy* weight ablation using the identical observed peer scores.

This is a transparent weighted-mean experiment, NOT necessarily Reppo's real
protocol aggregation. An actual protocol replay needs the complete official
aggregation implementation and all its input data.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from rewardbench.research import read_jsonl


def build_weight_proxy(peer_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    fingerprints = set()
    for row in peer_rows:
        tid, cid, assessor = row.get('task_id'), row.get('candidate_id'), row.get('assessor_id')
        if not all(isinstance(v, str) and v for v in (tid, cid, assessor)):
            raise ValueError('Missing task/candidate/assessor ID')
        key = (tid, cid, assessor)
        if key in fingerprints:
            raise ValueError(f'Duplicate peer assessment: {key}')
        fingerprints.add(key)
        score, weight = row.get('score'), row.get('economic_weight')
        if isinstance(score, bool) or isinstance(weight, bool) or not all(isinstance(v, (int,float)) for v in (score, weight)):
            raise ValueError('Peer score and economic weight must be numeric')
        if not 0 <= score <= 100 or not 0 < weight < float('inf'):
            raise ValueError('Peer score or weight out of range')
        if not row.get('export_id') or not row.get('weight_definition'):
            raise ValueError('Missing protocol export provenance / weight definition')
        grouped[(tid, cid)].append(row)
    by_task = defaultdict(list)
    for (tid, cid), recs in grouped.items():
        by_task[tid].append((cid, {r['assessor_id'] for r in recs}))
    # Require exact same assessor set across the candidates of each task: this
    # prevents differences in judge composition masquerading as weighting effects.
    for tid, sets in by_task.items():
        if len(sets) < 2 or len({frozenset(x[1]) for x in sets}) != 1:
            raise ValueError(f'Task {tid} has unmatched assessor sets across candidates')
    scores = []
    for (tid, cid), recs in sorted(grouped.items()):
        unweighted = sum(r['score'] for r in recs) / len(recs)
        weighted = sum(r['score'] * r['economic_weight'] for r in recs) / sum(r['economic_weight'] for r in recs)
        for method, score in (('uniform_peer_mean', unweighted), ('economic_weighted_mean_proxy', weighted)):
            scores.append({'task_id':tid,'candidate_id':cid,'method':method,
                           'score':score,'source':'observed'})
    return scores


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assessments',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--audit-out',type=Path,required=True)
    a=p.parse_args()
    rows=read_jsonl(a.assessments)
    scores=build_weight_proxy(rows)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in scores),encoding='utf-8')
    audit={'assessments_sha256':hashlib.sha256(a.assessments.read_bytes()).hexdigest(),
           'assessment_count':len(rows),'score_rows':len(scores),
           'methodology':'Controlled identical-assessor weighted-mean proxy; not official protocol replay.',
           'limitations':['Economic weight provenance must be audited externally.',
                          'The real Reppo aggregation may use nonlinear mechanisms, community evidence or other components.',
                          'Successful proxy ranking does not prove that actual Reppo economics caused any result.']}
    a.audit_out.parent.mkdir(parents=True,exist_ok=True)
    a.audit_out.write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,indent=2))


if __name__=='__main__': main()
