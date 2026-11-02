"""Offline-only structural audit of the pre-frozen 50-pair cohort.

No network calls, re-selection, judge prompts, or public raw content output.
Requires local label-blind JSONL + private labels JSONL. A successful structural
audit does NOT grant privacy/rights clearance or paid-execution permission.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

INPUT_SHA = "35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39"
LABEL_SHA = "76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91"
EXPECTED = {"tie": 11, "weak": 20, "strong": 19}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def audit(inputs, labels, input_sha=INPUT_SHA, label_sha=LABEL_SHA):
    if digest(inputs) != input_sha or digest(labels) != label_sha:
        raise ValueError("Frozen SHA256 mismatch; cannot silently replace cohort")
    data, gold = rows(inputs), rows(labels)
    if len(data) != 50 or len(gold) != 50:
        raise ValueError("Expected exactly 50 input and label records")
    ids = [r.get("task_id") for r in data]
    gold_ids = [r.get("task_id") for r in gold]
    if any(not isinstance(i, str) or not i for i in ids + gold_ids):
        raise ValueError("Invalid task IDs")
    if len(set(ids)) != 50 or len(set(gold_ids)) != 50 or set(ids) != set(gold_ids):
        raise ValueError("Duplicate or unmatched task IDs")
    forbidden = {"preference_strength", "annotator_strengths", "human_labels", "gold", "label"}
    if any(forbidden.intersection(r) for r in data):
        raise ValueError("Human labels leaked into judge-facing records")
    count = collections.Counter()
    for r in gold:
        v = r.get("preference_strength")
        if type(v) is not int or not -3 <= v <= 3:
            raise ValueError("Invalid preference strength")
        count["tie" if v == 0 else ("weak" if abs(v) == 1 else "strong")] += 1
    if dict(count) != EXPECTED:
        raise ValueError("Stratum count mismatch")
    source_hashes = []
    for r in data:
        c = r.get("candidates")
        if not isinstance(c, list) or len(c) != 2 or [x.get("id") for x in c] != ["response_1", "response_2"]:
            raise ValueError("Invalid two-response candidate structure")
        if not isinstance(r.get("instruction"), str) or not r["instruction"].strip():
            raise ValueError("Missing instruction")
        if any(not isinstance(x.get("answer"), str) or not x["answer"].strip() for x in c):
            raise ValueError("Missing candidate answer")
        source_hashes.append((r.get("source") or {}).get("sample_hash"))
    if all(source_hashes) and len(set(source_hashes)) != 50:
        raise ValueError("Duplicate source sample hash")
    return {
        "status": "OFFLINE_STRUCTURAL_AUDIT_ONLY",
        "pairs": 50, "strata": dict(count),
        "input_sha256": input_sha, "labels_sha256": label_sha,
        "unique_source_hashes": len(set(source_hashes)) if all(source_hashes) else None,
        "privacy_and_rights_cleared": False,
        "paid_execution_authorized": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = audit(args.inputs, args.labels)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
