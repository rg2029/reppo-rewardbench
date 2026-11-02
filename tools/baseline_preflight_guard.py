"""Offline-only request manifest and budget validation. No network I/O.

A passing check is NOT execution authorization: paid workflows also need an
atomic persistent cross-run claim ledger and an audited historical inventory.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

BLOCKED = frozenset({"SUBMITTING", "RECONCILE", "SETTLED", "PARSE_ERROR", "RESERVED"})

def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")).hexdigest()

def request_fingerprint(*, source_hash, candidate_hash, model, rubric_hash, request_version):
    fields = (source_hash, candidate_hash, model, rubric_hash, request_version)
    if not all(isinstance(v, str) and v.strip() for v in fields):
        raise ValueError("All request fingerprint fields are required")
    return canonical_hash(fields)

def amount(value):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid currency amount") from None
    if not d.is_finite() or d < 0:
        raise ValueError("Currency amount must be finite and nonnegative")
    return d

def validate_offline_preflight(*, proposed, historical, frozen_input_hash,
                               observed_input_hash, existing_spend_usd,
                               uncertain_charges_usd, new_reserve_usd,
                               pilot_limit_usd="25", cumulative_limit_usd="500"):
    """Fail closed for unknown history, duplicate attempts or excessive spend."""
    if not frozen_input_hash or frozen_input_hash != observed_input_hash:
        raise ValueError("Frozen input hash mismatch")
    if not proposed:
        raise ValueError("No proposed requests")
    past = set()
    for row in historical:
        if row.get("status") not in BLOCKED:
            raise ValueError("Unknown or unresolved history status; fail closed")
        key = row.get("fingerprint")
        if not isinstance(key, str) or len(key) != 64:
            raise ValueError("History row missing fingerprint; fail closed")
        past.add(key)
    seen = set()
    for row in proposed:
        key = request_fingerprint(**row)
        if key in seen:
            raise ValueError("Duplicate within proposed manifest")
        if key in past:
            raise ValueError("Proposed request overlaps historical attempt")
        seen.add(key)
    spent = amount(existing_spend_usd)
    uncertain = amount(uncertain_charges_usd)
    reserve = amount(new_reserve_usd)
    if reserve > amount(pilot_limit_usd):
        raise ValueError("Proposed reservation exceeds pilot authorization")
    if spent + uncertain + reserve > amount(cumulative_limit_usd):
        raise ValueError("Proposed reservation exceeds cumulative ceiling")
    return {"request_count": len(proposed), "manifest_sha256": canonical_hash(proposed),
            "reserve_usd": str(reserve), "cumulative_worst_case_usd": str(spent + uncertain + reserve),
            "status": "OFFLINE_CHECK_ONLY_NOT_EXECUTION_AUTHORIZATION"}
