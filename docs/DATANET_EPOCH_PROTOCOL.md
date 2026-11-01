# Datanet epoch study: pre-registered descriptive test and proposed causal extension

**Study purpose:** Separate (a) whether Reppo's *complete* reward mechanism ranks coding-agent outputs better than contemporary alternatives from (b) whether repeated Datanet feedback makes rewards better **over epochs**. Only genuine verified labels and matched methods count toward findings.

## Study A — reward quality on a sealed task set (primary)

Use ≥100 independently verified public coding-agent tasks with two or more real model-generated patches (at least one test-pass, one test-fail per task). Freeze an immutable task manifest and verifier hashes before running judges; assign disjoint task-level splits. Use three conditions on *identical candidate texts*:

- S: one frozen external LLM judge.
- U: a predeclared ensemble of multiple judges (keep judge identity and model versions fixed) with uniform aggregation.
- R: the **complete Reppo Eval API composite**, including whatever primary, secondary and Datanet evidence it uses. Never split R into “primary only” and “secondary only” as if those were separate systems.

Endpoint: task-macro pairwise ranking accuracy against verified pass/fail. Also record request-to-settlement latency, dollar costs, peer count, coverage, availability of Datanet evidence, and adversarial error rates. No claim of economic causality without Study C.

## Study B — Datanet epoch drift (descriptive, secondary)

Track a controlled set of pre-registered **fixed public probes** and score it in every available epoch *together* with a contemporary baseline. Record a stable `epoch_id`, time window, `snapshot_id`, `snapshot_at`, full composite and baseline scores. Our `rewardbench.longitudinal` analyzer reports:

- task-macro accuracy for both methods in each epoch;
- method gap on a *four-cell matched panel* observed under both methods at both endpoints;
- change in gap and task-clustered exploratory 95% bootstrap interval;
- missingness and provenance; it rejects future snapshots and duplicate observations.

**Not causal:** fixed probes may themselves become known to Datanets, their public evaluation history can affect future results, and model/swarm participation may change. Observational rising signals are a *diagnostic*, not proof that repeated economic feedback improved the signal.

## Study C — isolated contribution of economic coordination (conditional)

Requires an approved *read-only* internal replay export and protocol version. Hold primary evaluator outputs, prompt/candidate, test label, Datanet snapshot and evaluation time **fixed**. Vary only the specified secondary/aggregation component:

1. Real protocol aggregate, re-run using the exact production algorithm.
2. Same inputs with approved “uniform/neutral” secondary weighting or disabled economic coordination, if mathematically well-defined.
3. Same inputs with shuffled secondary weights as a placebo, preserving total vote power.
4. Optional frozen-vs-updated Datanet signal snapshots on unseen probes, but only if replay supports historical as-of state.

Check replayed real score against the observed API score on a calibration set (tolerance specified by the engineer) before running ablations. The current arithmetic weighted-mean proxy is **not** a protocol replay and cannot establish causal economic contribution.

## Study D — downstream learning (separate gate)

If Study A yields a meaningful signal, consider a controlled LoRA policy-update experiment. Maintain exact same prompts, optimizer, candidate count, epochs, compute, seeds and verifier. The *sole* changed variable is reward function. Report held-out test success, compute dollars, update steps, training curves and runs with failures. DPO is offline preference tuning, **not** online RL; best-of-N is selection, **not** learning. Only a genuine online loop with weight updates can support online/inference-time RL wording.

## CLI for snapshot audit

```bash
python -m rewardbench.longitudinal \
  --tasks path/to/frozen_tasks.jsonl \
  --scores path/to/snapshot_scores.jsonl \
  --split test --method-a reppo_full --method-b uniform_ensemble \
  --out runs/epoch-audit.json
```

`frozen_tasks.jsonl` uses the same schema as `rewardbench.research`; each score observation must have:

```json
{"task_id":"task-1","candidate_id":"patch-a","method":"reppo_full","epoch_id":"epoch-77","epoch_index":77,"score":83.5,"source":"observed","scored_at":"2026-11-01T12:00:00Z","snapshot_at":"2026-10-31T00:00:00Z","snapshot_id":"opaque-state-hash","provenance_ref":"sha256-or-approved-log-id","datanet_id":"code-qa","evidence_basis":"community-pods"}
```

For a baseline, `datanet_id` and `evidence_basis` may be omitted; `method` can be `single_judge` or `uniform_ensemble`. For an API call that does **not** reveal an actual Datanet ID/snapshot, do not invent one: record `datanet_id:"not-available"`, `evidence_basis:"unknown"`, and **do not present the epoch findings as real Datanet dynamics**. Both `scored_at` and `snapshot_at` must be actual UTC times (not estimates), with snapshot no later than the score. `provenance_ref` points to a real stored log or immutable hash, not an invented ID. Missing historical snapshots will block this analysis until the engineer provides a read-only export.

No backfilled future data, undisclosed task edits or re-scoring after seeing holdout labels. A report must include raw count of eligible observations and all exclusions. Never publicly post sensitive customer or on-chain identity data without permission and de-identification review.
