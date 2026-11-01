"""Build a license-labelled Hugging Face smoke preview; NEVER a scientific benchmark.

The examples are original project scaffolding. Labels are manually checked and
are deliberately NOT represented as independently executed coding outcomes.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rewardbench.research import validate_tasks

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'examples' / 'pilot_cases.jsonl'
TARGET = ROOT / 'hf' / 'dataset' / 'data' / 'smoke_preview.jsonl'


def build():
    source = [json.loads(x) for x in SOURCE.read_text(encoding='utf-8').splitlines() if x.strip()]
    rows = []
    for task in source:
        rows.append({
            'task_id': task['task_id'],
            'split': 'smoke',
            'license': 'cc-by-4.0',
            'instruction': task['instruction'],
            'candidates': task['candidates'],
        })
    audit = validate_tasks(rows, strict=False)
    flat = []
    for task in rows:
        for candidate in task['candidates']:
            flat.append({
                'task_id': task['task_id'], 'split': 'smoke',
                'instruction': task['instruction'], 'candidate_id': candidate['id'],
                'candidate_text': candidate['answer'],
                'claimed_correctness': candidate['verified_correct'],
                'label_quality': 'manually-checked toy arithmetic, unverified by independent harness',
                'content_provenance': 'authored by Reppo RewardBench starter',
            })
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in flat), encoding='utf-8')
    print(f'Wrote {len(flat)} rows from {audit["tasks"]} smoke tasks to {TARGET}')


if __name__ == '__main__':
    build()
