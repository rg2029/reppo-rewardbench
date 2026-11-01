"""Checkpointed, one-at-a-time pilot runner. Standard library only.

Default behavior never calls the network. Live calls require --live and an API key.
Never run recurring paid jobs from this script without approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from rewardbench.reppo_adapter import ReppoAdapter, RewardRequest, summarize_settlement
from rewardbench.scoring import pairwise_ranking_accuracy, majority_scores
from rewardbench.stats import paired_bootstrap_delta

USD_PER_EVAL_DOCS = 0.01  # published 2026-11-01; actual account price must be checked
USD_PER_EVAL_SAFETY = 0.22  # conservative: founder previously indicated 22 cents/eval
PROJECT_CEILING_USD = 500.0


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(s) for s in f if s.strip()]


def save_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_state(run_dir: Path) -> dict:
    p = run_dir / "state.json"
    if not p.exists():
        raise RuntimeError(f"Missing {p}. Run prepare first.")
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(run_dir: Path, state: dict) -> None:
    save_json(run_dir / "state.json", state)


def prepare(input_path: Path, run_dir: Path, max_candidates: int, public_approved: bool) -> None:
    if not public_approved:
        raise RuntimeError("Pass --public-approved only after ensuring every task/candidate can be published")
    if (run_dir / "state.json").exists():
        raise RuntimeError("Run exists; choose a new --run-dir to preserve immutable evidence")
    rows = load_jsonl(input_path)
    if not rows:
        raise ValueError("No input tasks")
    seen = set()
    tasks = []
    entries = []
    for row in rows:
        tid = row.get("task_id")
        if not isinstance(tid, str) or not tid or tid in seen:
            raise ValueError("Nonunique or missing task_id")
        seen.add(tid)
        instruction = row.get("instruction")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("Missing instruction")
        candidates = row.get("candidates")
        if not isinstance(candidates, list) or len(candidates) < 2:
            raise ValueError("Each task needs at least two candidates")
        ids = set()
        for candidate in candidates:
            cid = candidate.get("id")
            if not isinstance(cid, str) or not cid or cid in ids:
                raise ValueError("Missing/duplicate candidate id")
            ids.add(cid)
            if candidate.get("verified_correct") not in (0, 1):
                raise ValueError("Independently verified correctness must be 0/1")
            if not isinstance(candidate.get("answer"), str) or not candidate["answer"].strip():
                raise ValueError("Missing candidate answer")
            if len(entries) < max_candidates:
                entries.append({
                    "task_id": tid, "candidate_id": cid,
                    "instruction": instruction, "answer": candidate["answer"],
                    "verified_correct": int(candidate["verified_correct"]),
                    "status": "READY"
                })
        tasks.append(tid)
    if max_candidates < 1:
        raise ValueError("max-candidates must be positive")
    content = input_path.read_bytes()
    save_state(run_dir, {
        "kind": "Reppo RewardBench PILOT -- not RL evidence",
        "source_path": str(input_path),
        "source_sha256": hashlib.sha256(content).hexdigest(),
        "source_public_approved": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "documented_cost_usd_per_eval": USD_PER_EVAL_DOCS,
        "conservative_safety_budget_usd_per_eval": USD_PER_EVAL_SAFETY,
        "entries": entries,
    })
    print(f"Prepared {len(entries)} candidate evaluations from {len(tasks)} tasks; "
          "API calls made: 0. Source frozen by SHA256.")


def count_financial(state: dict) -> tuple[int, float]:
    committed = sum(1 for e in state["entries"] if e["status"] in
                    ("SUBMITTING", "PENDING", "SETTLED", "FAILED", "RECONCILE"))
    estimate = committed * USD_PER_EVAL_SAFETY
    return committed, round(estimate, 4)


def status(run_dir: Path) -> None:
    state = load_state(run_dir)
    counts = {x: sum(e["status"] == x for e in state["entries"])
              for x in ("READY", "SUBMITTING", "PENDING", "SETTLED", "FAILED", "RECONCILE")}
    committed, estimate = count_financial(state)
    print("RUN:", run_dir)
    print("STATUS:", counts)
    print(f"Conservative reserved budget at $0.22/eval: ${estimate:.2f} "
          f"for {committed} submitted/attempted evaluations (published price is $0.01; verify billing)")
    if counts["PENDING"] or counts["RECONCILE"] or counts["SUBMITTING"]:
        print("BLOCK: an evaluation is pending or needs reconciliation; do not submit another")
    print("Research evidence: NOT ESTABLISHED until actual settled evaluations exist")


def submit_next(run_dir: Path, max_evals: int, max_spend_usd: float, live: bool,
                adapter: ReppoAdapter | None = None) -> None:
    state = load_state(run_dir)
    if any(e["status"] in ("PENDING", "SUBMITTING", "RECONCILE") for e in state["entries"]):
        raise RuntimeError("Resolve or poll existing pending/unknown submission before submitting")
    committed, _ = count_financial(state)
    if max_evals > 10 or max_spend_usd > PROJECT_CEILING_USD or max_evals < 1 or max_spend_usd < 0:
        raise RuntimeError("First smoke run hard-capped at 10 evals; project cap is $500")
    if committed >= max_evals or (committed + 1) * USD_PER_EVAL_SAFETY > max_spend_usd + 1e-9:
        raise RuntimeError("Explicit API count/dollar cap reached. No submission made.")
    next_entry = next((e for e in state["entries"] if e["status"] == "READY"), None)
    if not next_entry:
        print("No remaining READY entries")
        return
    print("NEXT:", next_entry["task_id"], next_entry["candidate_id"])
    if not live:
        print("PREVIEW ONLY. Add --live to submit one evaluation; it may consume credits.")
        return
    api = adapter or ReppoAdapter()
    if not api.key:
        raise RuntimeError("Set REPPO_API_KEY in a secure environment")
    next_entry["status"] = "SUBMITTING"
    save_state(run_dir, state)  # written BEFORE POST to avoid duplicate on crash
    try:
        response = api.submit(RewardRequest(
            next_entry["task_id"], next_entry["instruction"], next_entry["answer"]
        ))
    except Exception:
        next_entry["status"] = "RECONCILE"
        save_state(run_dir, state)
        raise RuntimeError("Submit failed or response uncertain. State marked RECONCILE. "
                           "Inspect account pending evaluations before retrying; "
                           "do not repeat POST blindly.") from None
    next_entry.update({"status": "PENDING", "eval_id": response["evalId"]})
    save_state(run_dir, state)
    print("SUBMITTED:", response["evalId"], "(one pending at a time; min 10-minute window)")


def poll_once(run_dir: Path, live: bool, adapter: ReppoAdapter | None = None) -> None:
    state = load_state(run_dir)
    pending = [e for e in state["entries"] if e["status"] == "PENDING"]
    if len(pending) != 1:
        raise RuntimeError("Exactly one pending evaluation needed; check status")
    e = pending[0]
    if not live:
        print("PREVIEW ONLY. Would poll", e["eval_id"])
        return
    api = adapter or ReppoAdapter()
    result = api.get(e["eval_id"])
    summary = summarize_settlement(result)
    if summary["status"] == "PENDING":
        print("PENDING; try polling again after settlement window closes")
        return
    e["status"] = summary["status"]
    e["observed"] = summary
    save_state(run_dir, state)
    print("RESULT:", e["task_id"], e["candidate_id"], summary["status"],
          "score", summary.get("score", "n/a"))


def report(run_dir: Path) -> None:
    state = load_state(run_dir)
    settled = [e for e in state["entries"] if e["status"] == "SETTLED"]
    grouped = {}
    for e in state["entries"]:
        grouped.setdefault(e["task_id"], []).append(e)
    data = []
    for tid, entries in grouped.items():
        if len(entries) < 2 or not all(e["status"] == "SETTLED" for e in entries):
            continue
        truth = [e["verified_correct"] for e in entries]
        outputs = [e["answer"] for e in entries]
        major = majority_scores(outputs)
        reppo = [e["observed"]["score"] for e in entries]
        peer = [e["observed"].get("uniform_peer_mean") for e in entries]
        data.append({
            "task_id": tid,
            "reppo_pairwise_accuracy": pairwise_ranking_accuracy(reppo, truth),
            "majority_pairwise_accuracy": pairwise_ranking_accuracy(major, truth),
            "equal_weight_peer_pairwise_accuracy": (
                pairwise_ranking_accuracy(peer, truth) if all(p is not None for p in peer) else None
            ),
        })
    def macro(key):
        xs = [t[key] for t in data if t[key] is not None]
        return round(sum(xs)/len(xs), 4) if xs else None
    spent = sum(e.get("observed", {}).get("credits_charged", 0) or 0 for e in settled)
    matched_uniform = [(t["reppo_pairwise_accuracy"], t["equal_weight_peer_pairwise_accuracy"])
                       for t in data if t["reppo_pairwise_accuracy"] is not None
                       and t["equal_weight_peer_pairwise_accuracy"] is not None]
    matched_majority = [(t["reppo_pairwise_accuracy"], t["majority_pairwise_accuracy"])
                        for t in data if t["reppo_pairwise_accuracy"] is not None
                        and t["majority_pairwise_accuracy"] is not None]
    summary = {
        "pilot_only": True,
        "no_reinforcement_learning_performed": True,
        "no_causal_identification_of_economic_weighting": True,
        "candidate_evaluations_settled": len(settled),
        "total_prepared_candidates": len(state["entries"]),
        "completed_tasks_with_two_or_more_settled_candidates": len(data),
        "tasks": data,
        "task_macro_pairwise_accuracy": {
            "reppo": macro("reppo_pairwise_accuracy"),
            "majority": macro("majority_pairwise_accuracy"),
            "uniform_peer": macro("equal_weight_peer_pairwise_accuracy"),
        },
        "exploratory_task_bootstrap": {
            "reppo_minus_uniform_peer": paired_bootstrap_delta(matched_uniform) if len(matched_uniform) >= 20 else None,
            "reppo_minus_majority": paired_bootstrap_delta(matched_majority) if len(matched_majority) >= 20 else None,
        },
        "actual_credits_charged": spent,
        "approx_usd_at_documented_credit_rate": round(spent / 10_000, 4),
        "warning": "Tiny pilot. No significance tests. Economic weights not observed, so no economic mechanism claim.",
    }
    save_json(run_dir / "report.json", summary)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--input", type=Path, default=Path("examples/pilot_cases.jsonl"))
    p.add_argument("--run-dir", type=Path, default=Path("runs/smoke"))
    p.add_argument("--max-candidates", type=int, default=10)
    p.add_argument("--public-approved", action="store_true")
    for command in ("status", "submit-next", "poll", "report"):
        q = sub.add_parser(command)
        q.add_argument("--run-dir", type=Path, default=Path("runs/smoke"))
        if command == "submit-next":
            q.add_argument("--max-evals", type=int, default=10)
            q.add_argument("--max-spend-usd", type=float, default=2.20)
            q.add_argument("--live", action="store_true")
        if command == "poll":
            q.add_argument("--live", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.input, args.run_dir, args.max_candidates, args.public_approved)
        elif args.command == "status": status(args.run_dir)
        elif args.command == "submit-next":
            submit_next(args.run_dir, args.max_evals, args.max_spend_usd, args.live)
        elif args.command == "poll": poll_once(args.run_dir, args.live)
        elif args.command == "report": report(args.run_dir)
    except (RuntimeError, ValueError, OSError) as exc:
        parser.exit(2, f"BLOCKED: {exc}\n")


if __name__ == "__main__":
    main()
