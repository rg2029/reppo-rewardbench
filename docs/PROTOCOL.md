# RewardBench Protocol v0.2 — preregistration draft

**Date:** 2026-11-01  
**Research organization:** Reppo Labs  
**Maximum planned experimental spend:** USD 500  
**Status:** Protocol under revision. The arithmetic API smoke check completed; the separate coding-agent pilot is not yet included as evidence.

## Question and falsifiable hypotheses

- **H1 (reward accuracy):** Reppo's reward rankings yield higher pairwise agreement with independently verified task outcomes than a single judge and majority self-consistency.
- **H2 (mechanism ablation):** On the *same candidate texts and independent judge outputs*, economic weighting exceeds uniform weighting in rank accuracy and/or robustness.
- **H3 (learning; optional):** Under matched model, optimizer, number of samples, number of updates and token/compute budget, policy updates trained on Reppo rewards improve sealed held-out success over a baseline reward.

No hypothesis is presumed true. Directional results, null results and confidence intervals must be reported.

## Order of experiments

We will check reward rankings against task outcomes before attempting an experiment with model-weight updates. Inference-time selection, offline preference training and online RL are distinct interventions; evidence for one does not establish results for another.

## Task construction

Initial vertical: constrained Python function-writing tasks with deterministic tests, or an equally verifiable small reasoning dataset. Use **licensed/publicly releasable** examples or internally authored tasks only. Reserve at least 20% as sealed holdout, using task-level split (no near-duplicate leakage). Target 100–200 tasks and 2–4 candidate answers per task if budget allows; minimum feasibility batch 20 tasks. No unverifiable synthetic task can be counted as an outcome label.

Generate multiple candidates from one frozen version of a model using recorded sampling parameters. Apply a fixed test harness with timeouts and sandbox isolation for code execution. Never run arbitrary submitted candidate code unsandboxed. Store verifiable outcomes; annotate ambiguous tasks separately and exclude from primary scoring.

## Protocol specificity

Primary and secondary evaluators are **roles in a single Reppo network**. The public Reppo condition must be the **complete** Eval API mechanism. The prior arm separation would incorrectly imply distinct external services. The published Datanet whitepaper addresses veREPPO/Pod voting across 48-hour epochs; founder testimony describes per-request evaluator swarms. Exact implementation equivalence is not established until the engineer verifies request-level aggregation and historical signal snapshots. See `docs/MECHANISM_SPEC.md` and `docs/DATANET_EPOCH_PROTOCOL.md`.

## Experimental arms

A. Ground-truth deterministic outcome (upper reference, not deployable in unlabelled settings).
B. Self-consistency vote over canonicalized answers (no judge model).
C. A single independent LLM judge, fixed prompt/model/temp.
D. Multiple independent judges + uniform aggregation.
E. **Complete Reppo Eval API**, including primary swarms, secondary veREPPO feedback and available Datanet evidence. Internal counterfactual ablations using the same primary judge outputs and Datanet snapshots are planned **separately** and require an approved protocol data export.

If the Eval API exposes only its final composite and not all relevant internal judgments/weights, arm E is an **opaque Reppo composite**, and D-versus-E cannot isolate economic weighting. Don't claim economics caused any improvement.

## Primary metrics

Pairwise correctness-ranking accuracy on pairs where one candidate passes independent tests and the other fails; ties count 0.5. Report task-clustered 95% bootstrap CI and exact numerator/denominator. Secondary: ROC-AUC, ECE (only when scores are calibrated probabilities), Kendall/Spearman on appropriate labels, adversarial false-positive rate, measured latency, API costs, and skipped/missing rates. Report abstentions, parse failures and timeouts; no silent dropping. Bootstrap by task to avoid treating repeated candidates as independent.

## Optional learning experiment (H3)

Train/update a small open-weight policy (e.g. LoRA) from **training-split** candidate comparisons with identical data/optimization across arms, different only in reward ranking. Evaluate held-out unseen tasks with deterministic tests, at least three seeds if budget permits. If $150 training cap cannot support defensible comparison, defer H3 rather than claiming to have tested RL. Preference fine-tuning such as DPO is a *learning experiment*, but is not equivalent to online RL; label it accurately. For an RL claim, use a genuine online policy-optimization loop with weight updates. Report hardware, duration, tokens, checkpoints, seeds and costs.

## Predeclared go/no-go gates

Gate 0: exact Reppo API request/response schema, auth, privacy/data retention, rate and cost caps established; dataset rights approved.
Gate 1: 10 live API calls match a deterministic contract, with reproducible logs and no personally identifying data.
Gate 2: 20-task feasibility run yields at least 95% parseable outcomes and stays under $75 cumulative paid spend.
Gate 3: after >=100 tasks, H1 effect direction, CI, error audit, and cost-efficiency reviewed. Do not claim success on a favorable point estimate alone. Advance H3 only with explicit remaining-budget signoff.

## Credibility controls

- Publicly timestamp the preregistered plan before examining holdout results.
- Keep model/temperature fixed, one scoring prompt per condition, no prompt tuning on sealed holdout.
- Record API version, judge version, aggregation parameters, exact dataset hashes, seed, cost and time.
- Address evaluator overlap/correlation; multiple instances of one model are not fully independent judges.
- Assess prompt injection, benchmark contamination and reward hacking explicitly.
- Disclose conflicts and missing logs; distinguish independent reproduction from internal findings.

## Deliverables

Source-controlled protocol, dataset cards, scoring harness, adapter, CSV/JSONL logs, statistical analysis, a negative/positive-results-neutral report, and (only if real weight updates executed) RL training/evaluation artifact. Publication or outreach requires human technical review.
