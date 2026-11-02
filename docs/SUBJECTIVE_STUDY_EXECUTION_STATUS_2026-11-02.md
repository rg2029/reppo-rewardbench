# Subjective RewardBench experimental status

**As of 2026-11-02 04:25 UTC.** Experimental infrastructure is live; no subjective performance finding is yet verified.

## One-time Reppo feasibility experiment

Live GitHub Actions run [41387487415](https://github.com/rg2029/reppo-rewardbench/actions/runs/41387487415) began at 04:15 UTC and was **in progress** at this record's freeze. Uses three privacy-reviewed HelpSteer2 preference pairs: human tie, weak preference, strong preference; six sequential Reppo submissions, one pending at a time, conservatively reserved `$1.32` (6 x $0.22). A prior $1.32 reserve and cumulative $500 ceiling remain the financial controls.

Judge-facing dataset SHA256 `7ad782e4a0de979cf55a000ea160c86a6072bf1aa35f09f7afe66f7621c56320`; human label file separate. The employee internal-communication prompt is excluded. Do not report a success rate until the live run and artifact audit complete. **Never rerun the paid GitHub Action or replay a POST lacking a confirmed response.**

## Follow-on 50-pair human preference cohort

Source-locked natural-prevalence public HelpSteer2 validation subset frozen by Actions run [41388265182](https://github.com/rg2029/reppo-rewardbench/actions/runs/41388265182).

- 50 pairs drawn from 241 eligible prefiltered validation examples; 11 human ties, 20 weak preferences, 19 strong preferences.
- The three earlier pilot pairs are **excluded by original source-content hash**; there is no shared candidate between the paid pilot and 50-pair follow-on.
- Source JSONL SHA256: `35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39`.
- Human label JSONL SHA256: `76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91`.
- No evaluations have run on these 50 examples. They remain **subject to privacy and upstream rights review**. The distribution is natural within the prefiltered eligible frame, not representative of all human interactions.

## External independent judges

Read-only model catalog and auth checks succeeded. Planned fixed baselines: `meta-llama/Llama-3.3-70B-Instruct` and `Qwen/Qwen3-235B-A22B-Instruct-2507`. The first one-time external judge workflow [41387965762](https://github.com/rg2029/reppo-rewardbench/actions/runs/41387965762) stopped at the first POST without a usable result, marked `RECONCILE`, and did **not** submit later requests. No comparison scores exist.

Read-only `/api/whoami-v2` inspection found the GitHub `HF_TOKEN` is fine-grained with only `discussion.write` as a global scope, **not** the `Make calls to Inference Providers` scope needed to access routed model inference. Until the token is explicitly replaced with appropriately scoped credentials, **do not launch another paid external baseline**. Do not rerun the failed workflow. The first request's billing status must be reconciled.

## Two different hypotheses

1. **Reward utility:** Reppo's final score agrees with independent human preferences or uncertainty more than fixed external judge baselines on matched, source-locked, privacy-approved examples. A tiny three-pair feasibility result cannot establish this.
2. **Economic causality:** Holding **the same underlying evaluator judgments, model versions, Datanet evidence, and final aggregation function fixed**, vary economic weights to test their marginal contribution against uniform or shuffled weighting. **This has not been tested**, because production allocation and aggregation traces are not available from the public Eval API. Engineer-authenticated exports are required.

No RL model updates, human tie calibration, matched external results, significant effect, or economic attribution have been demonstrated. Preserve null and negative findings.
