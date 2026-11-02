# Cross-domain reward evaluation: preregistration extension v0.1

**Date:** 2026-11-02. **Status:** protocol only; no BFCL, tau-bench, GAIA or AgentDojo Reppo outcomes collected. This extends, and does not retroactively modify, the frozen two-task coding feasibility pilot.

## Objective and controls

Determine whether Reppo's settled evaluation score distinguishes independently successful from unsuccessful **authentic agent outputs** across workflows. Compare the same candidates under (1) one fixed external LLM judge, (2) a genuinely independent, equal-weight external ensemble, and (3) the complete Reppo Eval API. Do not treat Reppo's returned peer averages as the independent ensemble. Do not attribute a difference to economic voting without a same-judgments replay with actual weights and aggregation inputs.

## Track selection

| Track | Primary source | Independent outcome | Main pitfall |
|---|---|---|---|
| Coding | SWE-bench Verified + public generated patches and archived verifier logs | Official isolated patch-test result | Archived labels must be audited/reexecuted; existing n=2 is selected for discordance |
| Tool use | Berkeley Function Calling Leaderboard (BFCL), pin dataset/evaluator version | Official AST/execution/category-specific verifier | Correct syntax is not always successful action; preserve tool schema and execution context |
| Customer service | tau-bench / tau2-bench, pin version | Simulator database state and policy constraints | Candidate must be a genuine trajectory; omit hidden goal state from judge prompt |
| Research | GAIA public development data only, subject to access terms | Official reference answer or permitted deterministic check | Gated content, answer leakage, and redistribution restrictions |
| Adversarial | AgentDojo, pin release and scenario | Legitimate task success and attacker success as distinct outcomes | Keep adversarial safety metric separate; do not conflate attack success with task success |

Useful upstream links: https://github.com/SWE-bench/SWE-bench ; https://gorilla.cs.berkeley.edu/leaderboard.html ; https://github.com/sierra-research/tau2-bench ; https://huggingface.co/datasets/gaia-benchmark/GAIA ; https://github.com/ethz-spylab/agentdojo .

## Frozen manifest

For every item store: domain, upstream revision, license/access constraints, task ID, candidate ID, model/run provenance, original candidate/trace hash, verifier output and version, independent outcome, visible task context, tool schema where relevant, and canonicalized evaluator input hash. Source all candidates from actual model runs; never fabricate failures by corrupting correct answers. Predefine sampling and exclusions before seeing Reppo scores. Hold out disjoint tasks. A pair is eligible only if one candidate independently succeeds and one fails; report selection attrition and original success prevalence separately.

Never send verifier labels, hidden tests, gold answers, private customer traces, or simulator target state to the judges. The API may publish submitted task text; only submit data permitted for public display. For long trajectories define deterministic trace encoding and truncation before scoring. If an input cannot faithfully represent the workflow within limits, record it as unsupported rather than silently replacing it with a subjective summary.

## Metrics

Primary per-domain task-macro pairwise ranking accuracy, ties counted 0.5. Report exact counts, task-clustered 95% confidence intervals when sufficiently sampled, full coverage denominators, failures, abstentions, latency, and actual billed cost. Also report false-positive acceptance of failed candidates, domain-specific calibration only if scores have probabilistic meaning, and adversarial task/attack outcomes separately. No pooled headline score without preregistered domain weights.

Economic weighting causal claims require a separate replay on identical evaluator judgments and Datanet snapshots with genuine production aggregation, comparing original weights to uniform and shuffled weights. Reward ranking and best-of-N selection are not RL training.

## Execution and cost gates

The **existing $500 overall ceiling includes all earlier reservations and baseline-model/compute costs**. Reconcile account billing and existing commitments before new paid runs. No spend is authorized by this document alone.

1. **Free preflight:** pin revisions, check redistribution and API-input suitability; collect at least five genuine, verified pass/fail pairs for BFCL and tau-bench. Validate GAIA access rights and AgentDojo safety labels. Record exclusion logs.
2. **Capped trial:** after runner changes and tests, at most 5 tasks x 2 candidates x 2 new domains = 20 Reppo calls; reserve $4.40 at the conservative $0.22/call assumption, excluding baseline judge costs. Current pilot runner has a hard 10-evaluation cap and must be deliberately extended and reviewed. One pending request per account; never retry uncertain submissions without reconciliation.
3. **Scale only after audit:** aim for at least 50 matched pairs/domain, then 100+ if feasible. Freeze a held-out evaluation set, run external fixed baselines on exactly the same candidate presentations, and publish null/negative findings.
4. **Release:** verify rights, hashes, billing, verifier provenance, missingness, errors, and reproducibility. Keep the academic manuscript synchronized with actual observed results; never claim a completed benchmark from a successful workflow.

## Current evidence boundary

As of the public report dated November 2, 2026, the two-task coding pilot had four settled evaluations and task-macro pairwise accuracy **0.25** (one tie, one incorrect ranking). Its upstream verifier labels have not been independently rerun. There are **no observed cross-domain results**. The earlier arithmetic smoke test scored a correct and incorrect response 100 and 0, respectively. Neither study isolates the economic mechanism or demonstrates RL improvement.
