"""Label-blind offline subjective scoring. Never makes paid API calls."""
import hashlib
import json
from pathlib import Path

FROZEN_SHA = "7ad782e4a0de979cf55a000ea160c86a6072bf1aa35f09f7afe66f7621c56320"
CRITERIA = [
    "Instruction adherence: follow the user's actual request and constraints; score 0-100.",
    "Factual reliability: accuracy, calibrated claims, and no unsupported assertions; score 0-100.",
    "Usefulness: relevance, clarity, completeness, and actionable detail; score 0-100.",
    "Safety and uncertainty: avoid harmful guidance and acknowledge uncertainty; score 0-100.",
]

def load_frozen(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_SHA:
        raise ValueError("Frozen artifact SHA mismatch")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows) != 6 or len({r["task_id"] for r in rows}) != 6:
        raise ValueError("Expected six unique pairs")
    for r in rows:
        if set(r) != {"task_id", "instruction", "candidates", "source"}:
            raise ValueError("Unexpected judge fields")
        if len(r["candidates"]) != 2 or any(set(c) != {"id", "answer"} for c in r["candidates"]):
            raise ValueError("Unexpected candidate fields")
    return rows

def submission(row, index):
    if index not in (0, 1):
        raise ValueError("Invalid candidate index")
    data = {"type": "answer", "payload": row["candidates"][index]["answer"],
            "context": row["instruction"], "criteria": CRITERIA, "settlementMinutes": 10}
    if len(data["payload"].encode()) > 50000 or len(data["context"].encode()) > 32000:
        raise ValueError("API size exceeded")
    return data

def analyze_pair(scores, human_strength, equivalence_margin=5):
    if human_strength not in range(-3, 4):
        raise ValueError("Invalid human label")
    if len(scores) != 2 or any(type(x) not in (int, float) or not 0 <= x <= 100 for x in scores):
        raise ValueError("Invalid scores")
    difference = scores[0] - scores[1]
    order = 0 if difference > 0 else 1 if difference < 0 else None
    stratum = "tie" if human_strength == 0 else "weak" if abs(human_strength) == 1 else "strong"
    agreement = None if human_strength == 0 else (0.5 if order is None else float(order == (0 if human_strength > 0 else 1)))
    return {"stratum": stratum, "margin": abs(difference), "equivalent": abs(difference) <= equivalence_margin,
            "predicted_index": order, "strict_agreement": agreement}
