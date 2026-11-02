"""One-time, capped Reppo coding-agent feasibility test.

Uses the frozen public SWE-bench artifact from run 41371862402.
Never retries uncertain submissions or silently drops unsettled results.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time

from rewardbench import pilot

EXPECTED_TASK_SHA = "d7c28e3a5b954c8dec5f28d6a821cc1f22d97e6379aa16230e315c959924b1f2"
EXPECTED_IDS = ("astropy__astropy-14182", "django__django-10973")
MAX_EVALS = 4
MAX_RESERVATION_USD = 0.88
PER_EVAL_WAIT_SECONDS = 25 * 60


def main():
    src = Path("source-preflight/tasks.jsonl")
    manifest = Path("source-preflight/manifest.json")
    actual_sha = hashlib.sha256(src.read_bytes()).hexdigest()
    if actual_sha != EXPECTED_TASK_SHA:
        raise RuntimeError("Frozen dataset SHA mismatch: no API calls made.")
    prov = json.loads(manifest.read_text(encoding="utf-8"))
    if prov["task_sha256"] != EXPECTED_TASK_SHA or prov["candidate_count"] != 6:
        raise RuntimeError("Frozen manifest mismatch: no API calls made.")
    rows = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = rows[:2]
    if tuple(t["task_id"] for t in selected) != EXPECTED_IDS:
        raise RuntimeError("Frozen task selection differs from predeclared IDs.")
    for task in selected:
        if len(task["candidates"]) != 2 or sorted(c["verified_correct"] for c in task["candidates"]) != [0, 1]:
            raise RuntimeError("No independently verified pass/fail contrast.")
        if task["source"]["dataset"] != "princeton-nlp/SWE-bench_Verified":
            raise RuntimeError("Unexpected dataset provenance.")
        for cand in task["candidates"]:
            if hashlib.sha256(cand["answer"].encode("utf-8")).hexdigest() != cand["patch_sha256"]:
                raise RuntimeError("Patch hash mismatch; no API calls.")
    if os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise RuntimeError("Rerunning a workflow with paid submissions is forbidden.")
    if not os.environ.get("REPPO_API_KEY"):
        raise RuntimeError("No API secret. Stop without submitting.")

    output = Path("runs/coding-agent-v1")
    output.mkdir(parents=True, exist_ok=False)
    input_path = output / "frozen_tasks.jsonl"
    input_path.write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in selected), encoding="utf-8")
    run_dir = output / "reppo"
    pilot.prepare(input_path, run_dir, max_candidates=MAX_EVALS, public_approved=True)
    print("Archived real coding-agent solutions: first 2 frozen SWE-bench tasks, 4 candidates.", flush=True)
    print("Spending guard: 4 API calls maximum, reserved USD 0.88, no auto top-ups.", flush=True)
    try:
        for index in range(MAX_EVALS):
            pilot.submit_next(run_dir, max_evals=MAX_EVALS, max_spend_usd=MAX_RESERVATION_USD, live=True)
            deadline = time.monotonic() + PER_EVAL_WAIT_SECONDS
            while True:
                pilot.poll_once(run_dir, live=True)
                state = pilot.load_state(run_dir)
                entry = state["entries"][index]
                if entry["status"] == "SETTLED":
                    print("Settled %d/%d: %s/%s, score %.1f" % (
                        index + 1, MAX_EVALS, entry["task_id"],
                        entry["candidate_id"], entry["observed"]["score"]), flush=True)
                    break
                if entry["status"] == "FAILED":
                    raise RuntimeError("Evaluation failed. Stop; do not continue.")
                if time.monotonic() > deadline:
                    raise RuntimeError("Evaluation remains pending after 25 minutes. Stop; do not submit another.")
                time.sleep(60)
        pilot.report(run_dir)
        print("Four-evaluation feasibility run completed; original verification records retained.", flush=True)
    finally:
        try:
            pilot.status(run_dir)
            pilot.report(run_dir)
        except Exception as exc:
            print("Unable to prepare complete report; checkpoints retained:", type(exc).__name__, flush=True)


if __name__ == "__main__":
    main()
