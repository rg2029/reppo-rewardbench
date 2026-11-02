# Reppo RewardBench project status — 2026-11-02, v0.5

**Release readiness:** Public scientific release **NOT READY**. Real coding-agent feasibility results recorded; not yet a controlled or adequately powered scientific study.

## Implemented and verified

- CPU-only standard-library reward-ranking analysis with matched tasks, coverage and task-level exploratory confidence intervals.
- Strict coding-agent candidate provenance / SWE-bench verification manifest importer; importer does **not** run patches or produce verifier outcomes.
- Reppo public API submit/read adapter and sequential 10-candidate smoke pilot with state persistence, public-data warning, reconciliation-on-ambiguity and dollar caps.
- **Integrated Reppo mechanism spec** based on founder explanation, public API docs and the published Datanet whitepaper; explicit uncertainty about production API aggregation.
- **Longitudinal Datanet diagnostic** with task-panel matching, snapshot timestamp validation, observed/simulated provenance, missingness and descriptive matched-baseline changes.
- **Pod vote replay of published whitepaper equations**; intentionally **not** described as a replay of production Eval API rewards.
- Hugging Face dataset preview and static report viewer released **publicly**, with only authored toy data and no scientific efficacy claim.
- **48 CPU tests passing** locally; deterministic synthetic demonstration fixtures run without network/credentials.

## Scientific status and resource use

- Actual Reppo authenticated API requests: **6 settled** (2 arithmetic smoke, 4 coding-agent feasibility).
- Archived third-party verifier-labeled coding-agent task pairs scored by Reppo: **2**. Upstream verifier records and patch hashes preserved; tests not rerun locally.
- Reppo coding-agent feasibility: **2 matched tasks**, task-macro pairwise accuracy **0.25**, one tie and one incorrect ranking. Equal mean of Reppo-provided peers **0.0** on these tasks, **not** a fixed external ensemble. No independent single-judge or fixed-ensemble matched comparison yet.
- Genuine economic protocol replay validated against real final reward: **0**
- Real cross-epoch signal snapshots: **0**
- Model RL weight updates: **0**
- Externally reproduced scientific findings: **none**
- Reppo API reported **880 + 1,760 = 2,640 credits charged** across both runs, approximately **$0.264** at the pilot's documented conversion (billing not reconciled). The coding-agent study reserved up to $0.88; overall founder-approved ceiling remains **$500**.

**The dataset preview is synthetic; real coding-agent scores are documented separately in [the feasibility report](CODING_AGENT_FEASIBILITY_2026-11-02.md).** The whitepaper replayer is an equation/unit-test tool, not a claim of field effectiveness.

## Sources audited

- https://reppo.xyz/Reppo_Whitepaper.pdf (Datanet, veREPPO, linear decay and 48-hour epoch equations)
- https://docs.reppo.ai/api/eval/overview
- https://docs.reppo.ai/api/eval/evaluations
- https://docs.reppo.ai/concepts/evaluation-api
- https://github.com/SWE-bench/SWE-bench
- https://github.com/SWE-bench/experiments

## Pending, in dependency order

1. **Credential and environment: completed:** GitHub, Hugging Face dataset and Space are public research previews. API and Hugging Face tokens are stored privately as GitHub Actions secrets, not repository files.
2. **API gate: integration passed:** Two non-confidential arithmetic evaluations settled, scores 100 and 0. API reported 880 credits; billing and underlying mechanism trace remain to be audited.
3. **Ground-truth dataset:** First two source-locked coding pairs and archived upstream verifier labels scored; audit third-party harness evidence, then expand to a natural-outcome sample and frozen holdout with appropriate rights.
4. **Baselines and results:** Collect fixed single-judge, uniform-ensemble and full-Reppo composite scores on the same candidates; audit score provenance and coverage.
5. **Internal mechanism validation:** One Reppo engineer reviews `docs/ENGINEER_EXPORT_REQUEST.md`, gives pseudonymized primary/economic trace and snapshot exports, documents exact aggregation code/version, and enables a faithful same-input counterfactual. The current proxy is *not* sufficient.
6. **Research release:** Researcher reviews independent labels, code, effect sizes, uncertainty, multiple comparisons, costs, leakage and ethical/rights issues. Publish dataset+code+Space only after that review. If the first result is null, publish it as null.
7. **Online learning experiment:** Remains a gated stretch goal; do not label reranking or DPO as inference-time RL.

## Current execution blockers

Remaining scientific blockers: reexecuted or independently audited verifier outcomes, larger samples representative of natural agent output, matched external judge baselines, authentic full-system weighting/snapshot traces. Reppo engineering attests the two Judging Judges HTML reports are real; on-chain provenance was not independently verified.
