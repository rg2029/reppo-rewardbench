# Reppo RewardBench — coding-agent operating rules

**Mission:** Evaluate whether independently generated economic feedback produces useful reward signals and, if justified by results, whether those rewards improve model learning. Never infer positive results from design alone.

**Budget:** USD $500 hard total planning ceiling, approved by founder for useful live tests once a new unexposed key is configured. Do not use the key previously pasted into conversation. First account-authenticated smoke run: 10 evaluations maximum and **$2.20 conservatively reserved**, using a $0.22 safety assumption while public docs say $0.01. Confirm actual billing in the console before spending. The founder has authorized spending up to $500 for experimental work; running paid evaluations additionally requires a secure, unexposed key, compatible account limits and a documented purchase ledger.

## Immediate tasks

1. Read `README.md`, `docs/PROTOCOL.md`, `docs/API_CONTRACT.md`, `docs/LIVE_PILOT.md`, and `docs/AGENT_HANDOFF.md`.
2. Run `python -m unittest discover -s tests -v`; fix errors without deleting or relaxing tests.
3. Produce a reviewable pull request for improved mock-contract tests, dataset rights checks and coding-task planning. Use CI to verify basic behavior.
4. Update `results/STATUS.md` with only measured or explicitly simulated results, costs, issues, and next gates.

## Official API rules

- The verified adapter is `rewardbench/reppo_adapter.py`. API submissions are asynchronous: one pending per account; minimum 10-minute window. Use `rewardbench/pilot.py` to checkpoint one request at a time.
- Never POST to a paid API, purchase compute, change credentials, or deploy ongoing background loops without explicit user approval. `--live` must not be set as a default.
- Do not retry ambiguous POSTs. Inspect `RECONCILE` and stop; duplicate costs or scientific double counting are unacceptable.
- Only submit authored/public data to the current Reppo Eval API. Submissions are publicly visible to other authenticated network users.
- Keep keys in the execution environment's secret manager, not code, logs, issue tickets, chat messages or repository files.
- Never publish an external repository, benchmark, result, or research paper without user approval.

## Scientific rules

- The 5 bundled arithmetic smoke tasks (10 candidate examples) are integration checks, NOT evidence for the economic-feedback or reinforcement-learning hypothesis.
- Generate or obtain genuinely verified coding tasks with licensing clearance, no benchmark-answer leakage and secure isolated code execution before running a reward-quality benchmark.
- Keep train/validation/holdout tasks disjoint and freeze the holdout before any prompt tuning or optimization.
- The public API exposes the Reppo composite and peer assessments but **not** full economic weighting or its causal ablation. Do not claim that economic weighting improved correctness without observing matched judge assessments and holding everything except weights fixed.
- No actual RL claim until weights/learning state are updated online and unseen-task performance is measured. DPO and reranking are distinct methods.
- Reporting must include negative results, null results, failures, costs, uncertainties and exact task counts.

## Exact starter prompt for Dots, Codex or Work

> Continue the Reppo RewardBench project from this repository. First run the CPU tests and review the official API contract and cost gates. Prepare the next reproducible scientific study without committing external spend or making live submissions. Keep the repo usable by a three-person startup with no A100 cluster. Report progress and blockers in results/STATUS.md, and ask only for permission needed to use the API key, spend within the preapproved cap, or publish.

## v0.4 integrated mechanism protocol

- Read `docs/MECHANISM_SPEC.md`, `docs/DATANET_EPOCH_PROTOCOL.md`, and `docs/ENGINEER_EXPORT_REQUEST.md`. Reppo primary LLM swarms, secondary veREPPO assessment, and Datanet signals form **one integrated intervention**. Never call `primary_only` a separate product, and never say the whitepaper proves the full current Eval API formula.
- Run `python tools/build_mechanism_demo.py` and the associated `longitudinal`/`datanet_replay` CLIs. Their fixtures must always retain `source: simulation` or `SIMULATION-ONLY`; never feed them into a scientific leaderboard.
- Distinguish Pod net-vote time-decay replay from per-request reward aggregation. Only claim the latter after a real source-verified replay matches observed final scores.
- A rising cross-epoch signal is an observational finding and may reflect public-probe contamination or changing evaluator mixtures; freeze and verify snapshots, and report baseline-adjusted matched accuracy changes without causal wording.