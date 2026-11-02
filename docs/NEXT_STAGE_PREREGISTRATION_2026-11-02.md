# Next-stage preregistration and execution gates (2026-11-02)

Status: **protocol only; zero new paid API requests**. This document adds gates without modifying the frozen 50-pair selection or the original six-settlement artifact.

## Existing evidence, including negatives
- The three deliberately selected subjective pilot pairs: tie 75/75, weak response-2 preference 70/75, strong response-2 preference 65/70. Original artifact has a reversed-sign analysis bug; corrected interpretation is post hoc. Do not present 3/3 as benchmark accuracy.
- Coding-agent pilot: task-macro accuracy 0.25 on two selected tasks (one tie, one wrong ranking). This is a negative result, not evidence of generalization.
- Two inspected voting reports showed no changed winner after equal-voter normalization. Their provenance is not independently authenticated.
- Existing Hugging Face baseline attempt has ambiguous first POST and insufficient Inference Providers token scope. No retry without invoice reconciliation, credentials, and new explicit approval.

## Gate A: offline cohort audit (no external requests)
1. Preserve source revision `990b2711a36180dd19d9c94b8627844866f8982a`, judge-input SHA256 `35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39`, hidden-label SHA256 `76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91`. Do not regenerate or change selection.
2. Produce an attrition table for all 448 upstream validation records, the 241 eligible records, and the 50 frozen records. Record deterministic exclusion precedence, duplicate-content collisions, answer/prompt lengths, language, sensitive material, rights, and source overlap with the three pilot pairs. A review flag is not permission to publish text.
3. Independently inspect original annotation direction and strength. Keep ties and annotator disagreement. Separate private label manifest from label-blind judge inputs; public audit should contain hashes and aggregate counts, not private raw text.
4. For any uncleared frozen row, mark **not evaluated** and preserve its denominator. Do not substitute a convenient row.

## Gate B: independent judge preregistration
- Fixed judges proposed: `meta-llama/Llama-3.3-70B-Instruct` and `Qwen/Qwen3-235B-A22B-Instruct-2507`, **only if** exact model revisions and permitted provider availability are verified read-only. If unavailable, publicly amend protocol *before* any results are viewed.
- Each judge scores each response independently on a frozen 0-100 rubric; no human label, pair ID, other response, Reppo score, or competing judge output in the request. Preserve deterministic presentation order and document decoding settings, output schema, refusals, truncation and parser behavior.
- Compute pair margin `score(response_2)-score(response_1)`. On non-ties, signed agreement is 1 if margin sign matches human sign, 0.5 for zero margin, otherwise 0. On ties, report exact equality and within-five-point equivalence **separately**, not as non-tie wins.
- Primary comparison: paired difference in non-tie agreement of Reppo composite vs fixed judge A. Secondary: judge B, equal-weight mean of matched A/B scores, tie equivalence, weak/strong strata, coverage, absolute margins, latency and invoice-verified USD cost. All comparisons use identical frozen examples; missing responses count toward coverage and never silently receive substitute scores.
- Report exact paired discordance counts and uncertainty intervals; use exploratory two-sided paired permutation or exact McNemar test where appropriate, and disclose multiplicity for secondary comparisons. Fifty examples are an estimation cohort, not a superiority claim.
- Do not make paid requests until baseline token scope, ambiguous prior charge, model availability, frozen rubric, budget ledger and explicit approval are documented.

## Gate C: causal mechanism test (separate from composite agreement)
Required per-example, authenticated, access-controlled trace:
`evaluation_id`, `input_hash`, `timestamp`, `aggregation_version`, `judge_id_pseudonym`, `judge_model_version`, `raw_judgment`, `normalization_parameters`, `evidence_hash`, `economic_weight`, `weight_source_event_ids`, `eligibility`, `final_score`, `rounding_rule`, and proof of provenance for weights and events. No keys, personal data, or confidential evidence in public docs.

1. Reproduce production final score from authenticated judgments and actual weights; if reconstruction fails, stop and report a trace mismatch.
2. Hold *exactly the same* eligible judges, judgments, evidence, normalization, aggregation code and rounding fixed. Change only actual weights to equal weights; then preseeded shuffled weights. If the production aggregation has non-weight-dependent nonlinear components, keep those fixed too and disclose them.
3. Compare pairwise agreement and coverage for actual vs uniform vs shuffled weights; provide per-pair transitions and uncertainty, including regressions. If weights are endogenous to judge quality, this is a controlled replay/ablation, **not randomized causal identification** of the full economic coordination process.
4. If no trace is obtainable, report **economic weighting untested**. A `uniform_peer_mean` across variable internal peers is not a valid fixed-judge or same-judgments ablation.

## Budget and release rules
- Founder cumulative research ceiling: **$500**, inclusive of earlier live calls, reservations and ambiguous provider charges. No additional spend authorized by this document.
- Prior subjective pilot: 2,640 credits, estimated $0.264 not invoice-verified; conservative reservation $1.32. Reconcile all other charges before allocating new budget.
- Never rerun Actions 41387487415 or retry an ambiguous paid POST. Keep checkpoint IDs and original artifacts immutable.
- Publish failures, ties, uncertainty, selection/clearance attrition, unfavorable comparisons and conflicts of interest. Reppo composite agreement and economic coordination advantage must be separate claims.
