"""Fail-closed, persistent cross-run Hugging Face request ledger.

Only the git-pushed main-branch record authorizes sending a request. Persist
RESERVED and SUBMITTING *before* network calls, and never retry any record,
including RECONCILE. This module never sends inference requests itself.
GitHub workflow concurrency provides serialization; a rejected git push stops
the caller. Git history is the source of truth, not ephemeral Actions artifacts.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
from tools.baseline_preflight_guard import request_fingerprint

ROOT = Path("research_ledger/hf_subjective_50")
TERMINAL = {"SETTLED", "PARSE_ERROR", "RECONCILE"}
STATES = {"RESERVED", "SUBMITTING"} | TERMINAL

def git(*args):
    return subprocess.run(["git", *args], check=True, text=True,
                          capture_output=True).stdout.strip()

def ledger_file(fingerprint):
    if len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
        raise ValueError("Invalid fingerprint")
    return ROOT / (fingerprint + ".json")

def require_clean_main():
    if os.getenv("GITHUB_ACTIONS") != "true" or os.getenv("GITHUB_RUN_ATTEMPT") != "1":
        raise RuntimeError("Ledger writes restricted to first-attempt GitHub Actions jobs")
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Persistent reservations require main branch checkout")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Tracked worktree dirty; cannot claim paid work")

def persist(record, *, creating=False):
    """Commit and push only this fingerprint's JSON file; any conflict aborts."""
    require_clean_main()
    fingerprint = record["fingerprint"]
    destination = ledger_file(fingerprint)
    if creating and destination.exists():
        raise RuntimeError("Request already claimed; never retry")
    if not creating and not destination.exists():
        raise RuntimeError("Missing existing claim; fail closed")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(".tmp")
    temp.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, destination)
    git("add", "--", str(destination))
    git("commit", "-m", f"audit: reserve or record HF request {fingerprint[:12]} [{record['status']}]")
    # Non-fast-forward fails closed if another job claimed or updated the branch.
    git("push", "origin", "HEAD:refs/heads/main")

def claim(request_fields, study_id, *, persist_fn=persist):
    fingerprint = request_fingerprint(**request_fields)
    if ledger_file(fingerprint).exists():
        raise RuntimeError("Request already recorded; never retry")
    record = {"fingerprint": fingerprint, "study_id": study_id, "request": request_fields,
              "status": "RESERVED", "attempts": 0}
    persist_fn(record, creating=True)
    return record

def transition(record, status, *, persist_fn=persist, details=None):
    if status not in STATES:
        raise ValueError("Unknown state")
    old = record["status"]
    allowed = {"RESERVED": {"SUBMITTING", "RECONCILE"},
               "SUBMITTING": TERMINAL}
    if status not in allowed.get(old, set()):
        raise RuntimeError("Terminal or invalid state transition; never retry")
    updated = {**record, "status": status}
    if status == "SUBMITTING":
        updated["attempts"] = 1
    if details:
        # Do not persist prompt, token, candidate text, private labels or raw judge output.
        permitted = {"score", "usage", "provider_request_id", "finish_reason", "error_category"}
        if not set(details).issubset(permitted):
            raise ValueError("Sensitive or unapproved ledger fields")
        updated["result_metadata"] = details
    persist_fn(updated, creating=False)
    return updated

def inspect_history():
    if not ROOT.exists():
        return []
    result = []
    for path in sorted(ROOT.glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("fingerprint") != path.stem or row.get("status") not in STATES:
            raise RuntimeError("Malformed ledger record")
        result.append({"fingerprint": row["fingerprint"], "status": row["status"]})
    return result
