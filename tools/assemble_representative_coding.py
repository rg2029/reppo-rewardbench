"""Freeze a label-unselected sample of public coding-agent patch pairs.

Unlike the first two-task feasibility run, selection NEVER conditions on whether
either agent passed. Outcomes are read only after candidate eligibility checks;
all eligible success/success, fail/fail and discordant pairs are retained.
Labels are saved for analysis but withheld from Reppo request payloads.

This script is read-only, makes no Reppo calls and never executes candidate code.
Upstream verifier records should be independently audited before publication.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request

import boto3
from botocore import UNSIGNED
from botocore.config import Config

from assemble_coding_pilot import MODEL_A, MODEL_B, REPO_LICENSE, DATASET, BUCKET, sha, fetch_tasks, s3_get, candidate_report

SEED = "reppo-rewardbench-label-blind-v1-2026-11-02"
TARGET_TASKS = 8
PER_REPO_LIMIT = 3
PATCH_MAX_BYTES = 9000
ISSUE_MAX_BYTES = 9000


def selection_key(row):
    return (hashlib.sha256((SEED + ":" + row["instance_id"]).encode("utf-8")).hexdigest(),
            row["instance_id"])


def candidate_patch(client, model, task_id):
    key = model[1] + "/logs/" + task_id + "/patch.diff"
    try:
        raw = s3_get(client, key)
    except (client.exceptions.NoSuchKey, KeyError):
        return None
    if not (60 <= len(raw) <= PATCH_MAX_BYTES):
        return None
    try:
        patch = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not patch.startswith("diff --git ") or "\x00" in patch:
        return None
    return {"patch": patch, "sha256": sha(raw),
            "key": "s3://" + BUCKET + "/" + key}


def main():
    out = Path("runs/representative-coding-preflight")
    out.mkdir(parents=True, exist_ok=False)
    client = boto3.client("s3", config=Config(signature_version=UNSIGNED,
                                              connect_timeout=6, read_timeout=12, retries={"max_attempts":2}))
    revision, rows = fetch_tasks()
    rows = sorted(rows, key=selection_key)
    selected, seen_repos, screening = [], {}, {"eligible":0,"ineligible":0}
    for task in rows:
        if len(selected) >= TARGET_TASKS:
            break
        repo = task.get("repo")
        tid = task.get("instance_id")
        prompt = task.get("problem_statement")
        if not isinstance(tid,str) or repo not in REPO_LICENSE or seen_repos.get(repo,0) >= PER_REPO_LIMIT:
            continue
        if not isinstance(prompt,str) or not (100 <= len(prompt.encode("utf-8")) <= ISSUE_MAX_BYTES):
            continue
        # Inspect BOTH patch sizes and applications first. Neither outcome determines eligibility.
        patches = [candidate_patch(client, model, tid) for model in (MODEL_A,MODEL_B)]
        if any(p is None for p in patches):
            screening["ineligible"]+=1
            continue
        if patches[0]["sha256"] == patches[1]["sha256"]:
            screening["ineligible"]+=1
            continue
        reports = [candidate_report(client, model, tid) for model in (MODEL_A, MODEL_B)]
        if any(r is None for r in reports):
            screening["ineligible"]+=1
            continue
        screening["eligible"]+=1
        row = {
            "task_id": tid,
            "split": "exploratory",
            "license": REPO_LICENSE[repo],
            "instruction": (f"Repository: {repo}\nBase commit: {task.get('base_commit')}\n"
                            f"Reported issue:\n{prompt}\n\nAssess whether the proposed patch solves the issue. "
                            "Do not assume a plausible patch passes executable tests."),
            "source": {"dataset":DATASET,"dataset_revision":revision,"repo":repo,
                       "base_commit":task.get("base_commit"),"instance_id":tid},
            "candidates": [],
        }
        for model, patch, report in zip((MODEL_A,MODEL_B), patches, reports):
            row["candidates"].append({
                "id":model[0],"answer":patch["patch"],"model_id":model[2],
                "verified_correct":int(report["status"]),
                "patch_sha256":patch["sha256"],"patch_archive_s3":patch["key"],
                "verification":{"method":"archived-upstream-SWE-bench-harness",
                                "artifact_sha256":report["raw_sha256"],
                                "archive_report_s3":"s3://"+BUCKET+"/"+report["key"]},
            })
        selected.append(row)
        seen_repos[repo]=seen_repos.get(repo,0)+1
        # Log eligibility, not the labels; do not inspect scores before freezing.
        print(f"Selected {len(selected)}/{TARGET_TASKS}: {tid} [{repo}], labels withheld from logs.", flush=True)
    if len(selected) != TARGET_TASKS:
        raise RuntimeError(f"Only {len(selected)} of {TARGET_TASKS} eligible pairs. No paid API calls made.")
    output = out/"tasks.jsonl"
    output.write_text("".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in selected),encoding="utf-8")
    counts = {"pass_pass":0,"fail_fail":0,"discordant":0}
    for row in selected:
        a,b=[c["verified_correct"] for c in row["candidates"]]
        counts["pass_pass" if a+b==2 else "fail_fail" if a+b==0 else "discordant"]+=1
    manifest = {
        "selection_seed":SEED, "selection_rule":"sort public 500-task dataset by sha256(seed:task_id); take first 8 with both applied distinct patches, verified archived reports, within source/size/rights caps, WITHOUT conditioning on outcomes",
        "dataset":DATASET,"dataset_revision":revision,"source_repository_licenses":REPO_LICENSE,
        "agent_runs":[{"model":m[2],"prefix":m[1]} for m in (MODEL_A,MODEL_B)],
        "task_count":len(selected),"candidate_count":2*len(selected),
        "tasks_sha256":sha(output.read_bytes()),"outcome_strata":counts,
        "screening_counts":screening, "sampling_frame":"subset with public patches and verifiers for both agents, <=9kB patches; not representative of all coding agents",
        "notes":["Archived upstream verifier reports have not been independently rerun.",
                 "Selection is label-unconditioned but eligibility excludes missing/unapplied/oversized patches.",
                 "No paired task ranking can be calculated on fail/fail or pass/pass pairs; evaluate calibration and false acceptance separately.",
                 "The frozen exploratory set is NOT a sealed benchmark holdout.",
                 "Potential benchmark contamination; do not use selected tasks to tune judge prompts after seeing outcomes."]
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("FROZEN PRE-SCORING MANIFEST",json.dumps({"sha256":manifest["tasks_sha256"],
          "tasks":len(selected),"outcome_strata":counts},sort_keys=True),flush=True)


if __name__=="__main__":
    main()
