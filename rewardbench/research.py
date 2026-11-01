"""Offline, task-clustered reward-ranking study. No secrets, network or arbitrary code execution.

Input source consists of curated task-candidate examples with verified binary labels.
Scores are separately collected under identical held-out tasks. This module never
manufactures reward scores, runs untrusted code, or fills in missing observations.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from rewardbench.scoring import pairwise_ranking_accuracy
from rewardbench.stats import paired_bootstrap_delta


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_tasks(rows: list[dict], *, strict: bool = False) -> dict:
    """Check task-level splits, provenance, labels, and candidate IDs.

    Strict demands a verifier artifact reference; it cannot prove that the
    referenced tests actually passed. Independent execution must happen upstream.
    """
    if not rows:
        raise ValueError("Dataset is empty")
    seen_tasks = set()
    n_candidates = 0
    by_split = defaultdict(int)
    for task in rows:
        tid = task.get("task_id")
        if not isinstance(tid, str) or not tid or tid in seen_tasks:
            raise ValueError(f"Missing or duplicate task_id: {tid}")
        seen_tasks.add(tid)
        split = task.get("split")
        if split not in ("smoke", "train", "validation", "test"):
            raise ValueError(f"Invalid split on {tid}: {split}")
        if not isinstance(task.get("instruction"), str) or not task["instruction"].strip():
            raise ValueError(f"Task {tid} has no instruction")
        if not isinstance(task.get("license"), str) or not task["license"].strip():
            raise ValueError(f"Task {tid} missing dataset rights/license")
        candidates = task.get("candidates")
        if not isinstance(candidates, list) or len(candidates) < 2:
            raise ValueError(f"Task {tid} needs at least two candidates")
        ids = set()
        outcomes = []
        for cand in candidates:
            cid = cand.get("id")
            if not isinstance(cid, str) or not cid or cid in ids:
                raise ValueError(f"Missing or duplicate candidate id on {tid}")
            ids.add(cid)
            outcome = cand.get("verified_correct")
            if type(outcome) is not int or outcome not in (0, 1):
                raise ValueError(f"Candidate {tid}/{cid} requires integer verified_correct 0/1")
            if not isinstance(cand.get("answer"), str) or not cand["answer"].strip():
                raise ValueError(f"Candidate {tid}/{cid} missing answer")
            if strict:
                verifier = cand.get("verification")
                if not isinstance(verifier, dict) or verifier.get("method") not in (
                    "deterministic-tests", "reviewer-adjudication"
                ) or not isinstance(verifier.get("artifact_sha256"), str) or len(verifier["artifact_sha256"]) != 64:
                    raise ValueError(f"Candidate {tid}/{cid} lacks independently verifiable record")
            outcomes.append(outcome)
            n_candidates += 1
        if 0 not in outcomes or 1 not in outcomes:
            raise ValueError(f"Task {tid} must have passing and failing candidates")
        by_split[split] += 1
    return {"tasks": len(rows), "candidates": n_candidates, "tasks_by_split": dict(by_split),
            "strict_verification_metadata_checked": strict}


def validate_scores(rows: list[dict], tasks: list[dict]) -> dict:
    permitted = {(t["task_id"], c["id"]) for t in tasks for c in t["candidates"]}
    seen = set()
    by_method = defaultdict(int)
    for row in rows:
        key = (row.get("task_id"), row.get("candidate_id"))
        method = row.get("method")
        if key not in permitted or not isinstance(method, str) or not method:
            raise ValueError(f"Invalid score task/candidate/method: {key}, {method}")
        signature = (method, *key)
        if signature in seen:
            raise ValueError(f"Duplicate method/task/candidate score: {signature}")
        seen.add(signature)
        score = row.get("score")
        if isinstance(score, bool) or not isinstance(score, (float, int)) or not math.isfinite(score):
            raise ValueError(f"Score must be finite numeric: {signature}")
        if not 0 <= score <= 100:
            raise ValueError(f"Score must be 0..100: {signature}")
        if row.get("source") not in ("observed", "simulation"):
            raise ValueError("Scores must explicitly say observed or simulation")
        by_method[method] += 1
    return {"scores": len(rows), "by_method": dict(by_method)}


def score_study(tasks: list[dict], score_rows: list[dict], *, split="test", seed=20261101) -> dict:
    validate_tasks(tasks)
    validate_scores(score_rows, tasks)
    if split not in ("smoke", "train", "validation", "test"):
        raise ValueError("Invalid requested split")
    by_method = defaultdict(dict)
    origins = defaultdict(set)
    for record in score_rows:
        m = record["method"]
        by_method[m][(record["task_id"], record["candidate_id"])] = record["score"]
        origins[m].add(record["source"])
    selected = [t for t in tasks if t["split"] == split]
    if not selected:
        raise ValueError(f"No tasks for split {split}")
    per_task = {}
    for task in selected:
        tid = task["task_id"]
        truth = [c["verified_correct"] for c in task["candidates"]]
        per_task[tid] = {}
        for method, values in by_method.items():
            keys = [(tid, c["id"]) for c in task["candidates"]]
            if not all(key in values for key in keys):
                per_task[tid][method] = None
                continue
            per_task[tid][method] = pairwise_ranking_accuracy([values[k] for k in keys], truth)
    methods = sorted(by_method)
    coverage = {}
    for m in methods:
        available = [per_task[t["task_id"]][m] for t in selected if per_task[t["task_id"]][m] is not None]
        coverage[m] = {
            "tasks_complete": len(available),
            "tasks_expected": len(selected),
            "coverage": len(available) / len(selected),
            "macro_task_pairwise_accuracy": (sum(available) / len(available)) if available else None,
            "source_types": sorted(origins[m]),
        }
    comparisons = {}
    for i, a in enumerate(methods):
        for b in methods[i+1:]:
            pairs = [(per_task[t["task_id"]][a], per_task[t["task_id"]][b])
                     for t in selected if per_task[t["task_id"]][a] is not None
                     and per_task[t["task_id"]][b] is not None]
            if not pairs:
                continue
            deltas = [x-y for x,y in pairs]
            comparisons[f"{a}__minus__{b}"] = {
                "n_matched_tasks": len(pairs),
                "matched_delta": sum(deltas) / len(deltas),
                "a_wins": sum(x > y for x,y in pairs),
                "b_wins": sum(x < y for x,y in pairs),
                "ties": sum(x == y for x,y in pairs),
                "bootstrap": paired_bootstrap_delta(pairs, seed=seed) if len(pairs) >= 2 else None,
            }
    any_simulated = any("simulation" in origins[m] for m in methods)
    return {
        "research_question": "Can independently coordinated feedback improve reward quality?",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "split": split, "n_tasks": len(selected), "n_score_rows": len(score_rows),
        "methods": coverage, "comparisons": comparisons,
        "simulation_present": any_simulated,
        "scientific_evidence": ("NOT ESTABLISHED: demonstration-only/simulated" if any_simulated or split == "smoke"
                                else "OBSERVATIONAL REWARD QUALITY ONLY; no RL or economic causal attribution"),
        "caveats": ["Completeness can vary by method; all pairwise comparisons use matched tasks.",
                    "Bootstraps are task-clustered exploratory 95% intervals.",
                    "Verification records and independent task execution must be audited externally.",
                    "Scores do not demonstrate online RL or causal economic weighting."],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Offline, auditable score study")
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--scores", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--split", default="test", choices=["smoke", "train", "validation", "test"])
    p.add_argument("--strict", action="store_true", help="Require verification artifact hashes")
    a = p.parse_args()
    tasks = read_jsonl(a.tasks)
    audit = validate_tasks(tasks, strict=a.strict)
    result = {"task_validation": audit, "task_file_sha256": _hash(a.tasks)}
    if a.scores:
        score_rows = read_jsonl(a.scores)
        report = score_study(tasks, score_rows, split=a.split)
        report["score_file_sha256"] = _hash(a.scores)
        result["study"] = report
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
