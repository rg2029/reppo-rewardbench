# Reppo RewardBench project status — 2026-11-01, v0.4

**Release readiness:** Public scientific release **NOT READY**. Working offline research and integration scaffold, no genuine research outcomes yet.

## Implemented and verified

- CPU-only standard-library reward-ranking analysis with matched tasks, coverage and task-level exploratory confidence intervals.
- Strict coding-agent candidate provenance / SWE-bench verification manifest importer; importer does **not** run patches or produce verifier outcomes.
- Reppo public API submit/read adapter and sequential 10-candidate smoke pilot with state persistence, public-data warning, reconciliation-on-ambiguity and dollar caps.
- **Integrated Reppo mechanism spec** based on founder explanation, public API docs and the published Datanet whitepaper; explicit uncertainty about production API aggregation.
- **Longitudinal Datanet diagnostic** with task-panel matching, snapshot timestamp validation, observed/simulated provenance, missingness and descriptive matched-baseline changes.
- **Pod vote replay of published whitepaper equations**; intentionally **not** described as a replay of production Eval API rewards.
- Hugging Face dataset preview and static Space deployed privately; the Space was confirmed running.
- **48 CPU tests passing** locally; deterministic synthetic demonstration fixtures run without network/credentials.

## Scientific status and resource use

- Actual Reppo authenticated API requests: **2**, both settled (one toy arithmetic task)
- Actual independently tested coding-agent task results: **0**
- Observed single judge / uniform ensemble / full Reppo study rows: **0**
- Genuine economic protocol replay validated against real final reward: **0**
- Real cross-epoch signal snapshots: **0**
- Model RL weight updates: **0**
- Externally reproduced scientific findings: **none**
- Reppo API reported **880 credits charged** on the integration smoke test. Approximately **$0.088** at the documented conversion, not yet verified against account billing; original project ceiling remains **$500**.

**All bundled example scores are simulated or mock data**. The whitepaper replayer is an equation/unit-test tool, not a claim of field effectiveness.

## Sources audited

- https://reppo.xyz/Reppo_Whitepaper.pdf (Datanet, veREPPO, linear decay and 48-hour epoch equations)
- https://docs.reppo.ai/api/eval/overview
- https://docs.reppo.ai/api/eval/evaluations
- https://docs.reppo.ai/concepts/evaluation-api
- https://github.com/SWE-bench/SWE-bench
- https://github.com/SWE-bench/experiments

## Pending, in dependency order

1. **Credential and environment: completed:** Private GitHub and Hugging Face repos created, API and Hugging Face tokens stored as GitHub Actions secrets (not repository files).
2. **API gate: integration passed:** Two non-confidential arithmetic evaluations settled, scores 100 and 0. API reported 880 credits; billing and underlying mechanism trace remain to be audited.
3. **Ground-truth dataset:** Obtain 100+ appropriately licensed coding-agent task/candidate pairs with genuine official isolated-verifier logs and a frozen holdout, ideally from public SWE-bench Verified submissions after rights checks.
4. **Baselines and results:** Collect fixed single-judge, uniform-ensemble and full-Reppo composite scores on the same candidates; audit score provenance and coverage.
5. **Internal mechanism validation:** One Reppo engineer reviews `docs/ENGINEER_EXPORT_REQUEST.md`, gives pseudonymized primary/economic trace and snapshot exports, documents exact aggregation code/version, and enables a faithful same-input counterfactual. The current proxy is *not* sufficient.
6. **Research release:** Researcher reviews independent labels, code, effect sizes, uncertainty, multiple comparisons, costs, leakage and ethical/rights issues. Publish dataset+code+Space only after that review. If the first result is null, publish it as null.
7. **Online learning experiment:** Remains a gated stretch goal; do not label reranking or DPO as inference-time RL.

## Current execution blockers

Remaining scientific blockers: independently verified coding-agent tasks and candidate patches, matched baseline scores, authentic full-system weighting/snapshot traces. Reppo engineering attests the two Judging Judges HTML reports are real; on-chain provenance was not independently verified.
