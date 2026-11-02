# Evaluating Economic Coordination for AI Judgment: Feasibility Evidence from Human Preferences and Verifiable Outcomes

**Working manuscript, 2026-11-02. Not submitted. Not peer reviewed.**
Author: Raghav Rmadya (Reppo Labs). Disclosure: the author is affiliated with the system under evaluation.

## Abstract

Reliable evaluation of AI outputs is difficult when quality depends on subjective human preference, and when plausibly worded outputs can be wrong under verifiable tests. Economically coordinated evaluation networks offer a potential alternative to fixed model judges, but evidence of agreement with external labels must be distinguished from evidence that economic coordination itself adds value. We describe an auditable comparison protocol for a production evaluation API, independent fixed-model judges, and uniform ensembles. In an intentionally selected three-pair human-preference feasibility study, the Reppo API returned equal scores on one human tie (75/75), and favored the human-preferred response on two non-ties (70/75 and 65/70). Separately, a two-task coding-agent pilot achieved task-macro pairwise accuracy of 0.25, demonstrating failure to reliably rank checked outcomes in this small test. These observations are feasibility checks, not superiority estimates: no matched fixed-judge baseline or authenticated same-judgment economic-weight ablation has yet been completed. We preregister a 50-pair frozen, eligibility-filtered natural-prevalence cohort for further evaluation and specify the provenance required to study economic weighting. Our contribution at this stage is an explicit measurement framework and transparent reporting of initial positive and negative evidence, including unresolved identification limits.

## 1. Introduction

Evaluators of AI outputs often face two different problems. First, there may be no single objectively correct answer, and human annotators themselves may disagree. Second, an answer may appear convincing even when it fails an independently checkable task. Both problems complicate the use of an LLM judge score as a quality target for training or deployment. Networked evaluation with economic signals offers one design alternative. However, a high final score that agrees with an external label does not show that the economic component caused this agreement.

This study therefore separates (i) **composite agreement**: whether the final Reppo evaluation score correctly orders alternatives according to held-out human preferences or outcome verifiers, and (ii) **weighting attribution**: whether the production economic weights improve the result when the same underlying evaluator judgments are held fixed. A separate trial, with economic incentives manipulated ex ante, would be needed to identify incentive effects on which judgments are produced.

## 2. Study design

We compare independently scored candidates on the same original task/prompt. For each response we collect a final Reppo composite score, a score from fixed external judge A, a score from independently fixed external judge B, and a mean of A and B only when both model scores are complete. All judges must use a frozen rubric and answer presentation; gold human preference, competing answer, other model outputs and Reppo score are hidden from judge prompts.

For a pair, define margin as score(response 2) minus score(response 1). For non-tie human preferences, agreement is 1 if the signs agree, 0.5 for an exactly zero judge margin, and 0 otherwise. Ties are evaluated separately with exact equality and a prespecified within-five-point score band. We report coverage, missingness, signed margins, weak/strong preference strata and paired uncertainty intervals. Estimates from very small deliberately selected pilots are not representative accuracy estimates.

The follow-on cohort is selected deterministically from NVIDIA HelpSteer2 validation preference records at upstream revision `990b2711a36180dd19d9c94b8627844866f8982a` within an eligibility-filtered frame. It has 50 frozen pairs drawn from 241 eligible of 448 validation records: 11 ties, 20 weak and 19 strong. Frozen input SHA256: `35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39`. Hidden label SHA256: `76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91`. These are **preparation records, not evidence that 50 live evaluations have occurred**. Row-level clearance and an attrition audit remain necessary. The follow-on cohort is not representative of all production prompts.

## 3. Preliminary observations

### 3.1 Human-preference feasibility

In GitHub Actions run `41387487415`, six distinct Reppo API calls settled across three intentionally selected pairs. In a human tie, response scores were 75/75 (margin 0). For a weak preference favoring response 2, scores were 70/75 (margin +5); for a strong preference favoring response 2, 65/70 (margin +5). Thus both non-ties agreed in direction and the tie was scored equally. Importantly, the original machine-readable report had a reversed-sign comparison bug and labeled both non-ties incorrect. The above interpretation is a disclosed post-hoc correction of the analysis using unchanged raw scores and frozen labels. The source selection was deliberately stratified, making any population-level accuracy inference invalid.

Six settlements reported 2,640 credits total. A nominal $0.264 conversion is not invoice-reconciled; the conservative reservation was $1.32. No fixed external judge outcomes or economic mechanism replays exist for these pairs.

### 3.2 Verifiable coding outcomes

A prior coding-agent feasibility pilot evaluated two deliberately chosen tasks. One pair was tied and one incorrectly ranked, yielding task-macro pairwise accuracy 0.25 under the study's convention that a judge tie scores 0.5. Verifier labels came from archived task evidence rather than independently rerun tests. This unfavorable finding is retained, not pooled with subjective results.

### 3.3 External baseline execution status

The earlier external baseline workflow `41387965762` terminated after an ambiguous first provider POST. Its checkpoint showed one RECONCILE, 11 READY and zero SETTLED completions; no matched baseline scores were obtained. Subsequent billing screenshots showed no visible November usage on the account, but this does not prove the request was unprocessed. This request must not be retried automatically. The old script was found to target an earlier stratified cohort, rather than the frozen 50-pair follow-on; it has been fail-closed pending a redesigned workflow.

## 4. Testing the economic mechanism

A valid conditional aggregation replay requires authenticated, per-evaluation and per-evaluator records: original input hash, primary judgments, eligible evaluator set, any score-normalization parameters, evidence, production aggregation code/version, actual economic weights with provenance, timestamps and final output. First reproduce production scores with actual weights. Then, with **the identical judgments and code**, recompute scores under equal weights and preseeded shuffled weights. Report disagreements and regressions rather than only improved examples.

Such a replay estimates the role of weights conditional on the observed judgments. It is **not** randomized causal evidence of how incentives affect evaluator participation, effort, selection or reporting. Two previously inspected voting reports showed no winner change under equal-voter normalization and remain insufficient to validate the economic hypothesis.

## 5. Limitations and research integrity

The subjective feasibility sample has only three deliberately selected pairs, and the coding pilot only two tasks. The human-preference examples are heterogeneous: one strong example concerns factual accuracy, rather than purely subjective taste. The source eligibility filter affects generalizability; individual annotator disagreement and license/privacy review are outstanding. The external baseline is not complete, and no same-judgment economic aggregation trace has been authenticated. Reppo Labs' affiliation with the studied system constitutes a conflict to disclose. API credits and billing amounts require reconciliation. We cannot claim benchmark superiority, improved reinforcement learning, calibrated probabilities, or an economically causal advantage.

## 6. Next-stage preregistered analysis

Complete the frozen 50-pair privacy/eligibility audit. Obtain exact provider and fixed-judge versions read-only; freeze scoring prompts, parsing and missing-response handling. After the historical ambiguous request, token permissions, atomic cross-run deduplication and spend ledgers are resolved, execute only distinct preregistered calls, with no automatic retries, and publish complete pairwise tables with uncertainty. Independently obtain the authenticated Reppo mechanism trace and conduct a same-judgment aggregation replay. A separate untouched transfer set will be needed before broader claims.

## Availability and reproducibility

Public repository: https://github.com/rg2029/reppo-rewardbench

Original subjective run: https://github.com/rg2029/reppo-rewardbench/actions/runs/41387487415

Original coding pilot: `results/CODING_AGENT_FEASIBILITY_2026-11-02.md`

Audit and protocols: `docs/SUBJECTIVE_FEASIBILITY_AUDIT_2026-11-02.md`, `docs/SUBJECTIVE_FOLLOWON_PROTOCOL_2026-11-02.md`, `docs/NEXT_STAGE_PREREGISTRATION_2026-11-02.md`, `docs/BASELINE_EXECUTION_BLOCKER_AUDIT_2026-11-02.md`.

**Bibliography pending**: before an arXiv submission, add source-verified citations and a related-work comparison covering RewardBench, RewardBench 2, HelpSteer2, LLM-as-a-judge reliability and preference learning. This working draft must not be misrepresented as submission-ready.
