"""Frozen 50-pair independent judge runner. OFFLINE by default.

Paid execution requires a separately audited clearance/budget gate, an
account-wide historical reconciliation, and persistent successful git pushes
before every POST. Not connected to any paid Actions workflow by default.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from tools.audit_frozen_subjective_50 import audit
from tools.baseline_preflight_guard import validate_offline_preflight, request_fingerprint, amount
from tools.persistent_hf_request_ledger import claim, transition, inspect_history
from tools.run_subjective_external_baselines import (
    MODELS, MODEL_RESERVE_USD, MAX_OUT_TOKENS, catalog, fixed_prompt, submit_once
)

STUDY_ID = "subjective-natural-50-fixed-judges-2026-11-02"
DATA = Path("runs/subjective-natural-preflight")
CONTROL = Path("research_controls/hf_subjective_50_gate.json")
OUTPUT = Path("runs/subjective-natural-fixed-judges")
PILOT_MAX_PAIRS = 3    # 3 * 2 answers * 2 judges = 12 POSTs, only when unblocked
PILOT_MAX_POSTS = PILOT_MAX_PAIRS * 2 * len(MODELS)
FROZEN_INPUT_HASH = "35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39"
FROZEN_LABEL_HASH = "76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91"

def load_gate():
    gate = json.loads(CONTROL.read_text(encoding="utf-8"))
    if gate.get("study_id") != STUDY_ID:
        raise RuntimeError("Wrong gate / study ID")
    return gate

def make_manifest(selected):
    """Deterministic *first three* frozen rows; no results-based selection."""
    entries = []
    for item in selected:
        for i, candidate in enumerate(item["candidates"]):
            for model in MODELS:
                # Input content and model/rubric version should be fixed by study protocol.
                from tools.baseline_preflight_guard import canonical_hash
                fields = {
                    "source_hash": canonical_hash({"instruction": item["instruction"],
                                                     "source": item.get("source")}),
                    "candidate_hash": canonical_hash(candidate["answer"]),
                    "model": model,
                    "rubric_hash": canonical_hash(fixed_prompt(item, i)[0]["content"]),
                    "request_version": "natural-50-v1-temp0-64tokens"
                }
                entries.append({"task_id": item["task_id"], "candidate_id": candidate["id"],
                                "model": model, "fingerprint": request_fingerprint(**fields),
                                "request": fields})
    if len({e["fingerprint"] for e in entries}) != len(entries):
        raise RuntimeError("Repeated request in manifest")
    return entries

def write_summary(payload):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "preflight_summary.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paid", action="store_true", help="Requires independently completed gate")
    args = parser.parse_args()
    inspected = audit(DATA / "judge_inputs.jsonl", DATA / "human_labels.jsonl")
    raw = [json.loads(x) for x in (DATA / "judge_inputs.jsonl").read_text(encoding="utf-8").splitlines()]
    # Do not read gold labels into external-scoring process.
    selected = raw[:PILOT_MAX_PAIRS]
    entries = make_manifest(selected)
    if len(entries) != PILOT_MAX_POSTS:
        raise RuntimeError("Unexpected request count")
    history = inspect_history()
    summary = {"study_id": STUDY_ID, "frozen_sha256": inspected["input_sha256"],
               "pair_count": len(raw), "pilot_pair_count": len(selected),
               "planned_post_count": len(entries),
               "planned_fingerprint_sha256": __import__("tools.baseline_preflight_guard",
                        fromlist=["canonical_hash"]).canonical_hash([e["fingerprint"] for e in entries]),
               "historical_ledger_entries": len(history), "mode": "PAID" if args.paid else "DRY_RUN",
               "status": "NOT_EXECUTED"}
    if not args.paid:
        summary["reason"] = "Offline structural validation only; no model or billing requests"
        write_summary(summary)
        print(json.dumps(summary, sort_keys=True))
        return
    gate = load_gate()
    if gate.get("enable_paid_execution") is not True or gate.get("history_reconciled") is not True:
        raise RuntimeError("Paid gate disabled or global history not reconciled")
    if os.getenv("GITHUB_ACTIONS") != "true" or os.getenv("GITHUB_RUN_ATTEMPT") != "1":
        raise RuntimeError("Cannot execute paid runner outside first Actions attempt")
    cleared = gate.get("privacy_cleared_task_ids", [])
    if not isinstance(cleared, list) or not set(x["task_id"] for x in selected).issubset(set(cleared)):
        raise RuntimeError("Pilot rows have not been individually cleared for third-party submission")
    for key in ("historic_confirmed_usd", "uncertain_prior_charges_usd", "incremental_pilot_usd"):
        if gate.get(key) is None:
            raise RuntimeError("Unknown costs: no authorization to execute")
    validate_offline_preflight(
        proposed=[e["request"] for e in entries], historical=history,
        frozen_input_hash=FROZEN_INPUT_HASH, observed_input_hash=inspected["input_sha256"],
        existing_spend_usd=str(amount(gate["historic_confirmed_usd"]) + historical_reservations),
        uncertain_charges_usd=gate["uncertain_prior_charges_usd"],
        new_reserve_usd=str(current_reservation),
        pilot_limit_usd=str(gate["incremental_pilot_usd"]), cumulative_limit_usd="500"
    )
    if float(gate["incremental_pilot_usd"]) > 25:
        raise RuntimeError("Pilot authorization capped at $25 additional")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN unavailable")
    catalog(token)   # read-only model check
    summary["status"] = "IN_PROGRESS"
    write_summary(summary)
    for e in entries:
        source = next(r for r in selected if r["task_id"] == e["task_id"])
        idx = 0 if e["candidate_id"] == "response_1" else 1
        prompt = fixed_prompt(source, idx)
        if any(len(m["content"].encode("utf-8")) > 15000 for m in prompt):
            raise RuntimeError("Overlong request rejected")
        # Persistent global claim MUST reach remote main before POST.
        record = claim(e["request"], STUDY_ID, reserve_usd=str(MODEL_RESERVE_USD))
        record = transition(record, "SUBMITTING")
        try:
            answer = submit_once(e["model"], prompt, token) # ONE POST, NO RETRY
        except ValueError:
            transition(record, "PARSE_ERROR", details={"error_category": "INVALID_SCORE"})
            continue
        except Exception:
            # If this push fails, prior SUBMITTING claim still prevents replay.
            transition(record, "RECONCILE", details={"error_category": "AMBIGUOUS_POST"})
            raise RuntimeError("Ambiguous request; stop and never retry") from None
        transition(record, "SETTLED", details={
            "score": answer["score"], "usage": answer.get("usage"),
            "provider_request_id": answer.get("model_response_id"),
            "finish_reason": answer.get("finish_reason")
        })
    summary["status"] = "COMPLETED"
    write_summary(summary)
    print(json.dumps(summary, sort_keys=True))

if __name__ == "__main__":
    main()
