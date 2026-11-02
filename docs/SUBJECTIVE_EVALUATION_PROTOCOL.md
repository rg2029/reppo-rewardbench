# Subjective evaluation protocol: human preference, ambiguity, and disagreement

**Status:** preregistration design. No Reppo subjective-domain outcome has yet been measured.  
**Version:** 2026-11-02. This is a separate track from the frozen coding-agent pilot.

## Research question

Does Reppo's integrated evaluation signal agree with independent human preferences, and does it handle ambiguity and disagreement more appropriately than a matched fixed LLM judge or an external uniform ensemble?

This hypothesis is **not** that social or economic consensus is automatically correct. Annotators may reasonably disagree. The relevant outcome can be a distribution of judgments, not a single ground-truth answer.

The coding study is a comparison/control domain where a deterministic test oracle exists. It should not be treated as a proxy for Reppo's core value proposition in uncertain tasks.

## Primary data sources (candidates, not yet an approved frozen release)

1. [NVIDIA HelpSteer2 preference](https://huggingface.co/datasets/nvidia/HelpSteer2), CC BY 4.0. Human pairwise preferences scored from -3 to +3 (including ties), free-text reasoning, and multiple individual annotations. Its **validation** preference split provides an existing out-of-sample anchor; evaluate dataset rights and prompt contamination before release. Sample exact splits and repository SHA from HF API, then freeze before scoring.
2. [RewardBench 2](https://huggingface.co/datasets/allenai/reward-bench-2), ODC-BY, particularly the **Ties** and **Focus** subsets. Use an *independent transfer check*, not an internal training set. Third-party model output usage rights can differ from dataset rights.
3. [SummEval](https://github.com/Yale-LILY/SummEval), expert human ratings for relevance, coherence, consistency and fluency. Candidate because multiple raters enable inter-rater agreement and uncertainty analysis; check distribution rights and source-article licensing before use.
4. Task-specific expert/audience judgments on open-ended research and tool-use outcomes when public labels are inadequate. Do not present synthetic LLM opinions as independent human votes.

## Experimental design

**A. Small feasibility batch**: 6–12 human-annotated pairs, selected with a reproducible seed and frozen before Reppo calls. Report strata explicitly: decisive preference (absolute strength 2–3), weak preference (1), and tied preference (0). **This stratification is deliberately balanced, not representative of the naturally occurring distribution.**

**B. Natural-prevalence sample**: at least 30 additional prompt pairs sampled uniformly from eligible held-out data, without filtering on model preferences or observed Reppo outcomes. Report all inclusion/exclusion reasons, labels, source revision and exact denominator. Reuse of the feasibility set in this second sample is forbidden.

**C. External baselines**: a fixed single judge plus independent judges with a fixed equal-weight pooling rule. Prompt, temperature, model release date, API version, scoring range, text truncation and number of calls must be recorded. Reppo's own peer assessment mean is a useful diagnostic, **not** an independent external ensemble.

**D. Economic mechanism ablation**: reuse the identical primary judgments and accompanying Datanet evidence to reconstruct the actual reward under the production weighting, then recompute under equal economic weights. This is unavailable until independently approved trace and aggregation-code access is provided. A full-Reppo-versus-external-judge difference is not evidence of a causal economic-weighting effect.

Present each response independently in random order, using **exactly the same original user prompt and evaluation rubric**, without showing human preference labels, ratings, comparative justifications, chosen/rejected markers or model identities. Normalize scoring to a documented interval and score *each answer separately* to avoid feeding the pairwise target label into the judge. Randomization seed and position are frozen in the manifest. Check for candidate-length leakage, ranking by verbosity, and model self-preference.

## Outcomes: different measures for different questions

- **Strong and weak preferences**: strict pairwise agreement with human preferred response; ties made by a judge score 0.5. Report separately for strength 1 versus 2–3. Data with no majority agreement must be tabulated rather than dropped.
- **Human ties**: reward-score margin (absolute score difference), calibrated equivalence rate at a **predefined** margin threshold, false separation and ranking stability across candidate-order permutations. Avoid treating arbitrary high-confidence rank ordering as success in genuinely tied cases.
- **Human disagreement**: compare the distribution of individual human judgments to an evaluator's predicted probabilities where *actual* probability forecasts exist. Mean absolute score difference is **not** a calibrated probability; no Brier/ECE unless appropriate probability calibration is independently established.
- **Cross-rater uncertainty**: report individual annotations, majority strength and inter-annotator disagreement. Human preference is an operational reference standard, not an objective theorem.
- **Production utility**: selective acceptance/rejection under prespecified thresholds, abstention behavior, false confidence and resolution latency/cost.
- **Mechanism hypothesis**: only when the same input judges and evidence can be replayed; report effect sizes and task-clustered intervals on a sealed holdout.

Report per-domain stratification and overall sample composition. Do not pool coding, personal preferences, factuality, safety and creative work into one headline score. Three-stage multiplicity control and fixed thresholds must be registered before looking at held-out results.

## Instrumentation and release discipline

1. Freeze source identifier, commit/revision, prompt hashes, response hashes, split, selection seed and human-label extraction before API submission.
2. Read the publicly released dataset usage restrictions and ensure every example can be sent to a third-party evaluation API.
3. The existing coding adapter's correctness-specific rubric **is unsuitable** for human-preference research. A domain-appropriate rubric must be implemented and unit-tested without changing previous coding results.
4. Enforce one pending Reppo request per account, an explicit per-run count cap and conservative rate ceiling ($0.22 per call) with no blind resubmissions. The original total $500 ceiling remains in force. A staged pilot should cost much less; do not raise it because the research domain changed.
5. Archive every response, refusal, timeout, and credits field. Distinguish known settlement, unconfirmed charge, and approximate conversion. Make pilot outputs public only after license/privacy/evidence review.
6. Freeze a natural-distribution test split *before* inspecting results; exploratory outcome review must not determine which examples enter a future test.

## What would count as evidence?

A substantive positive result would be repeated agreement with independent human preferences on a sufficiently sized, untouched held-out sample, with confidence intervals and appropriate comparison to independent external judges, **and separately** a same-judgment economic replay showing improvement beyond uniform aggregation. The first can support reward utility; only the second can identify the role of economic weighting. Neither by itself proves better reinforcement learning.

Null or negative results belong in the paper with the same provenance and confidence reporting as positive ones.
