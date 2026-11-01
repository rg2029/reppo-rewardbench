"""Produce deterministic, explicitly synthetic data for testing ONLY."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rewardbench.longitudinal import score_epochs
from rewardbench.datanet_replay import replay_pod_votes
from rewardbench.research import read_jsonl

ROOT=Path(__file__).resolve().parent.parent
TASKS=ROOT/'examples/study_smoke_tasks.jsonl'
EPOCHS=ROOT/'examples/epoch_simulation_scores.jsonl'
VOTES=ROOT/'examples/datanet_simulation_votes.jsonl'


def encode_jsonl(rows):
    return ''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows)


def main():
    tasks=read_jsonl(TASKS)
    observations=[]
    for epoch in range(2):
        for t in tasks:
            for method in ('reppo_full','uniform_ensemble'):
                for c in t['candidates']:
                    correct=c['verified_correct']
                    # Entirely fabricated deterministic values; no empirical conclusions.
                    score=(75 if correct else 25) if method=='uniform_ensemble' else (
                        (80 if correct else 20) if epoch==1 else (20 if correct else 80))
                    observations.append({
                        'task_id':t['task_id'],'candidate_id':c['id'],
                        'method':method,'epoch_id':f'sim-epoch-{epoch}', 'epoch_index':epoch,
                        'score':score, 'source':'simulation',
                        'scored_at':f'2026-10-0{epoch+2}T00:00:00Z',
                        'snapshot_at':f'2026-10-0{epoch+1}T00:00:00Z',
                        'snapshot_id':f'SIMULATION-{method}-epoch{epoch}',
                        'provenance_ref':f'synthetic-mechanism-demo/{epoch}',
                        'datanet_id':'SIMULATION-ONLY' if method=='reppo_full' else None,
                        'evidence_basis':'unknown' if method=='reppo_full' else None})
    EPOCHS.write_text(encode_jsonl(observations),encoding='utf-8')
    votes=[{'datanet_id':'SIMULATION-ONLY','epoch_id':'sim-epoch-0','pod_id':'pod-1',
            'voter_pseudonym':voter,'direction':direction,'locked_reppo':amount,
            'lock_epochs':4,'max_lock_epochs':4,'gamma':2,
            'allocation_fraction':1,'elapsed_seconds':elapsed,'epoch_seconds':100}
           for voter,direction,amount,elapsed in [('voter-A',1,100,0),('voter-B',-1,150,50)]]
    VOTES.write_text(encode_jsonl(votes),encoding='utf-8')
    result=score_epochs(tasks,observations,split='smoke')
    replay=replay_pod_votes(votes)
    assert result['research_evidence']=='DEMONSTRATION ONLY'
    assert replay[0]['net_vote_decayed']==25
    print('Generated deterministic *simulated* mechanism fixtures. NO live results.')

if __name__=='__main__': main()
