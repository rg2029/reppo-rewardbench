# Frozen 50-pair independent baseline: implementation and release gate

Updated 2026-11-02. **New paid inference runs have NOT been launched.**

## Committed implementation

- `tools/assemble_subjective_natural.py` deterministically rebuilds the original frozen NVIDIA HelpSteer2 reference sample from revision `990b2711a36180dd19d9c94b8627844866f8982a` (read-only GET); the three previous Reppo pilot source pairs are excluded before sampling. Never alter its seed, eligibility rules or sample after observing results.
- `tools/audit_frozen_subjective_50.py` checks byte-for-byte SHA256 hashes, exactly 50 aligned pairs, unique source identifiers, label blindness, and 11 tie / 20 weak / 19 strong counts. A passing structural check is NOT a rights/privacy clearance.
- `tools/run_subjective_natural_baseline.py` uses **the first three frozen natural-prevalence pairs**, not the earlier stratified three-pair pilot; two independently fixed judge families; two single-answer calls per pair per model = at most **12 distinct pilot calls**. All 50 pairs are loaded and hash-verified. The pilot's first-three selection is fixed before seeing any model outcomes. Running without `--paid` has no inference POSTs.
- `tools/persistent_hf_request_ledger.py` commits **RESERVED** and then **SUBMITTING** records to GitHub's main branch and requires successful push before any POST. A failed push or already-present fingerprint blocks submission. SETTLED, PARSE_ERROR and RECONCILE are terminal and cannot be retried. Records include fingerprints, model identifiers, reservation amount, status and minimal returned metadata, never prompts, keys or raw human labels.
- `tools/baseline_preflight_guard.py` enforces frozen-input identity, no duplicate fingerprints, and $25 incremental / $500 cumulative guardrails. Prior reservations across runs are included in the new pilot limit.
- `.github/workflows/subjective-natural-offline-preflight.yml` is a **read-only / no-secret / no-paid** workflow: runs unit tests, rebuilds the pinned public corpus, validates hashes and performs a dry-run manifest. It publishes only an aggregate preflight summary.
- Legacy `tools/run_subjective_external_baselines.py` remains disabled at entrypoint due prior ambiguous POST.

## Required blockers before enabling paid execution

The tracked gate `research_controls/hf_subjective_50_gate.json` has `enable_paid_execution: false`, `history_reconciled: false`, empty privacy-clearance list, and null prior charges. Do **not** change these booleans without real evidence.

1. Inspect CI for the new offline workflow. If its pinned cohort cannot reproduce the two frozen hashes, stop and investigate, without selecting replacement rows.
2. Manually inspect and individually clear each of the first three frozen rows for privacy, prompt injection and rights to transmit to Hugging Face. Document any rejection and mark that row **not evaluated**, not silently substituted.
3. Reconcile all earlier research spend and the ambiguous first external provider request. Confirm updated HF token and both fixed models via **read-only** provider catalog; check model revisions and provider pricing before committing to the pilot.
4. Commit the audited historical ledger exclusions and budget starting balances. The old three-pair sample is excluded by source identity; no request previously marked RECONCILE may be resent.
5. Before any paid workflow is enabled, create a restricted, serialized first-attempt workflow with `contents: write`, `concurrency` on one shared group, tracked `main` checkout, authenticated git push, no retries, no duplicate invocation and no plaintext model inputs uploaded as public artifacts. This workflow does not exist yet.
6. Confirm revised budget reservation including all historical project costs: founder authorized **at most $25 additional** for the pilot, with the cumulative **$500 ceiling** unchanged. Reservations are not invoices.
7. Report all attempts, incomplete pairs and cost/latency failures, then separately compute the independent-judge comparisons. Do not infer economic causality from composite scores.

## Scientific status

Reppo's three selected subjective pilot comparisons (two directional alignments, one reproduced tie) are positive feasibility observations, not estimated benchmark performance. The two-task coding pilot had task-macro accuracy **0.25** and must remain in the paper. No external fixed-judge matched scores exist yet. The economic coordination hypothesis still requires authenticated same-judgment evaluator traces and exact production aggregation logic. A same-judgment replay isolates the contribution of weighting conditional on observed judgments; it does not identify the full causal effect of incentives on judge behavior.
