"""Reproducible toy *simulation*, explicitly not experimental evidence."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'examples'/'pilot_cases.jsonl'
target = ROOT/'examples'/'study_smoke_tasks.jsonl'
scores_out = ROOT/'examples'/'study_simulated_scores.jsonl'
rows=[]
scores=[]
for line in source.read_text(encoding='utf-8').splitlines():
    if not line: continue
    r=json.loads(line)
    rows.append({'task_id':r['task_id'],'split':'smoke','license':'cc-by-4.0',
                 'instruction':r['instruction'],'candidates':r['candidates']})
    for c in r['candidates']:
        for method in ('simulated_correct_judge','simulated_constant_judge'):
            score = 90 if c['verified_correct'] else 10
            if method=='simulated_constant_judge': score=50
            scores.append({'task_id':r['task_id'],'candidate_id':c['id'],'method':method,
                           'score':score,'source':'simulation'})
target.write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in rows), encoding='utf-8')
scores_out.write_text(''.join(json.dumps(s, sort_keys=True)+'\n' for s in scores), encoding='utf-8')
print(f'Generated {len(rows)} toy tasks and {len(scores)} simulated scores (not evidence).')
