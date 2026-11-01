"""Transparent research replay of *published Datanet Pod voting equations*.

Source: Reppo whitepaper (reppo.xyz/Reppo_Whitepaper.pdf), sections 4.2,
5.1-5.2 and 7.2-7.4. This is NOT the complete production Eval API reward
aggregation: primary evaluator swarms and request-level secondary mechanisms
are outside the published equations and require internal protocol code.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path


def finite_number(v, name, *, minimum=None, maximum=None, strict_min=False) -> float:
    if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v):
        raise ValueError(f'{name} must be a finite number')
    if minimum is not None and (v <= minimum if strict_min else v < minimum):
        raise ValueError(f'{name} out of range')
    if maximum is not None and v > maximum:
        raise ValueError(f'{name} out of range')
    return float(v)


def replay_pod_votes(rows: list[dict]) -> list[dict]:
    if not rows:
        raise ValueError('No votes provided')
    by_pod=defaultdict(list)
    seen=set()
    for r in rows:
        key=tuple(r.get(x) for x in ('datanet_id','epoch_id','pod_id','voter_pseudonym'))
        if any(not isinstance(v,str) or not v for v in key):
            raise ValueError('Datanet, epoch, Pod and voter pseudonym required')
        if key in seen:
            raise ValueError('Duplicate voter/Pod/epoch record; reconcile amendments upstream')
        seen.add(key)
        direction=r.get('direction')
        if direction not in (-1,1) or isinstance(direction,bool):
            raise ValueError('direction must be 1 or -1')
        locked=finite_number(r.get('locked_reppo'),'locked_reppo',minimum=0,strict_min=True)
        duration=finite_number(r.get('lock_epochs'),'lock_epochs',minimum=0,strict_min=True)
        max_duration=finite_number(r.get('max_lock_epochs'),'max_lock_epochs',minimum=0,strict_min=True)
        gamma=finite_number(r.get('gamma'),'gamma',minimum=1,strict_min=True)
        if duration>max_duration:
            raise ValueError('lock_epochs exceeds max_lock_epochs')
        fraction=finite_number(r.get('allocation_fraction'),'allocation_fraction',minimum=0,maximum=1)
        elapsed=finite_number(r.get('elapsed_seconds'),'elapsed_seconds',minimum=0)
        epoch_seconds=finite_number(r.get('epoch_seconds'),'epoch_seconds',minimum=0,strict_min=True)
        if elapsed>epoch_seconds:
            raise ValueError('Vote after epoch close')
        ve_power=locked*(duration/max_duration)**gamma
        effective=ve_power*fraction*(1-elapsed/epoch_seconds)
        by_pod[key[:3]].append((direction,effective,ve_power*fraction))
    results=[]
    for (datanet,epoch,pod), recs in sorted(by_pod.items()):
        weighted=sum(d*w for d,w,_ in recs)
        no_time_decay=sum(d*w for d,_,w in recs)
        headcount=sum(d for d,_,_ in recs)
        decisions=lambda x: 'accept' if x>0 else 'reject' if x<0 else 'tie'
        results.append({'datanet_id':datanet,'epoch_id':epoch,'pod_id':pod,
                        'voter_count':len(recs),
                        'net_vote_decayed':weighted,
                        'net_vote_no_decay':no_time_decay,
                        'net_vote_headcount':headcount,
                        'decision_decayed':decisions(weighted),
                        'decision_no_decay':decisions(no_time_decay),
                        'decision_headcount':decisions(headcount),
                        'replay_scope':'published Pod voting equations only; NOT Eval API composite',
                        'provenance':'Reppo Whitepaper sections 4.2,5.1,7.2-7.4'})
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--votes',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    with a.votes.open(encoding='utf-8') as f:
        rows=[json.loads(line) for line in f if line.strip()]
    result=replay_pod_votes(rows)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in result),encoding='utf-8')
    print(f'Replayed {len(result)} Pod/epoch outcomes (whitepaper equations only, not Eval API).')

if __name__=='__main__':main()
