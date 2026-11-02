# Independent-research release gates

This project is not a scientific publication merely because its code passes CI.

| Gate | Required before passing | Current status |
| --- | --- | --- |
| G0: working scaffold | Offline unit tests, API mock contract, non-secret config | **Pass (48 CPU tests; two API smoke evaluations completed separately)** |
| G1: real API smoke | One genuine settled evaluation + privacy and billing audit | **Passed API integration: two settled evaluations; billing reconciliation pending** |
| G2: validated reward dataset | >=100 licensed coding-agent tasks, authentic generated candidates, verifier artifacts, sealed holdout, independently checked | **Not done** |
| G3: reward baselines | Same candidates with Reppo, single judge, uniform peer baseline; complete coverage and confidence intervals | **Not done** |
| G4: economic causality | Genuine weights/stakes and aggregation procedure with same assessors/responses (plus sham/flat-weight controls) | **Not done** |
| G5: downstream causal outcome | Matched best-of-N and, if feasible, actual online weight-update RL with held-out tasks, cost and confidence intervals | **Not done** |
| G6: public release | independent audit, secret review, package hashes, HF dataset/Space, DOI/preprint only after findings | **Not done** |

**No unsupported claims:** Passing G3 doesn't prove RL; passing G4 doesn't prove RL; DPO isn't online RL. Best-of-N is inference-time selection not learning. External replication is not complete until another researcher successfully reproduces key analyses on the released artifacts.

## Primary endpoint and analysis unit

Task-macro pairwise accuracy when candidates have independently verified different outcomes; confidence intervals from resampling **tasks**, not individual pairs. Missing evaluations require explicit coverage denominators, failure rates and prespecified handling. Compare methods only on common matched tasks. Confidence intervals are exploratory at small n. Test set must be frozen with a recorded digest before observing method scores.

## Candidate provenance

For each task, retain source dataset commit and license, repository base commit, issue statement, candidate model ID/version, candidate sampling parameters, hash of patch/trace, verifier version and independently recorded pass/fail status. Never expose reference patch or hidden test in evaluator input.

## Deterministic verifier

Prefer the official SWE-bench harness for real coding-agent patches. Do not execute arbitrary candidate code in the app container or CI runners. SWE-bench documents Docker isolation and substantially greater CPU/RAM/disk requirements than this local fixture, so its actual execution is a future compute job, not a completed component.

## Independence of economic feedback

Self-reported assessor identity is not independent identity. Economic weighting is causal only when a controlled replay uses the **same assessor judgments** and changes precisely the weighting mechanism. If Reppo's final aggregate incorporates Datanet evidence or other hidden inputs, do not attribute its difference from an arithmetic mean to economics.
