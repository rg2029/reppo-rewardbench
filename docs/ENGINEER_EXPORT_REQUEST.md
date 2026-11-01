# Small read-only export request for the Reppo engineer

**This is not an infrastructure project.** A one-time anonymized JSONL export of ~20–50 consenting/public evaluation requests, their internal evaluator/vote evidence, and a few Datanet snapshots is enough to validate the harness. More comes only after the privacy/security audit. The founder already approved research access; **do not publish raw internal traces automatically**.

## Required per-request fields (one parent JSON object per evaluation)

- `eval_id_pseudonym` (stable pseudonym, no customer ID), `request_timestamp_utc`, `settled_timestamp_utc`, `protocol_version` (commit/hash), `public_test_task_id`.
- `candidate_sha256`, `criteria_sha256`, `full_score` (0–100), `final_decision`, `confidence`, `aggregate_calculation_hash`.
- `datanet_id_pseudonym` or null; `route` (`existing_signal`, `new_evaluation`, `mixed`, or `unknown`) **only if logged**; `datanet_epoch_id` and `snapshot_hash`/`snapshot_timestamp_utc` where available.
- `primary_assessments[]`: `primary_evaluator_pseudonym`, `model_family_or_hash`, `operator_pseudonym`, `score`, `time`, `reward_eligible` (if recorded). These need to be actual distinct evaluator observations, not synthetic records.
- `secondary_votes[]`: `voter_pseudonym`, `primary_evaluator_pseudonym`, `vote_direction`, `vote_weight_or_veREPPO_power`, `allocation`, `vote_timestamp`, `epoch_id`, `scoring_rule_version`. A secondary evaluation of a primary judge must remain attached to that primary judge.
- `aggregation_parameters`: enough to replay the actual **final** reward deterministically, including filters, abstentions, default rules, Datanet prior and any time decay.
- `billing_credits` and, if possible, compute/latency figures.

## Separate Datanet snapshot manifest

For each time point under study: `datanet_id_pseudonym`, `epoch_id`, `epoch_start_utc`, `epoch_end_utc`, `snapshot_id`, `snapshot_created_utc`, `signal_type`, `signal_digest`, `protocol_version`, `provenance_ref`. Do not substitute current-state queries for historical snapshots.

## Optional verifier file (public tasks only)

`task_id, candidate_id, source_dataset, license, base_commit, model_version, patch_sha256, verifier_artifact_sha256, verified_correct`. Ground truth **must not be fed into the evaluated prompt**. Use the official isolated task harness, never a raw `exec()` on the research laptop.

## Engineer checkboxes (15–30 minute async triage)

- [ ] Can every live result be replayed bit-for-bit (or within a documented tolerance) from the export?
- [ ] Can the *same* primary judgments be run through economic and neutral-weight counterfactual rules?
- [ ] Is veREPPO voting per request, per Datanet epoch, or both in this particular backend build?
- [ ] Does the public API actually expose/cache historical Datanet signal snapshots?
- [ ] Which fields are sensitive or unsafe to release, and which derived aggregates may be published?

If any answer is “no,” record it. The benchmark must be able to report *not identifiable* rather than manufacture a substitute. The current public API alone can support only the **full Reppo composite**, not credible internal economics ablations.
