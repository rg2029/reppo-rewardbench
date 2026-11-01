# Reppo RewardBench — open research starter (v0.4)

**Research question:** Can independent economic feedback improve reinforcement learning?

**Current status:** offline research methods + whitepaper equation replay + asynchronous Reppo API adapter + verified test harness + 10-candidate *sanity check* fixture. No live evaluations, RL optimization, or scientific conclusions yet. [Current status](results/STATUS.md).

## Updated mechanism-first design (v0.4)

**Reppo is one integrated full-system intervention**, not a collection of primary-only and secondary-only public products. The complete Eval API combines primary LLM/agent-swarm judgments, secondary veREPPO economic feedback, and possibly pre-existing Datanet evidence. The published [whitepaper](https://reppo.xyz/Reppo_Whitepaper.pdf) supports the epoch/net-vote equations but **does not establish the current live API aggregation formula**. See [mechanism specification](docs/MECHANISM_SPEC.md).

- `rewardbench/longitudinal.py`: optional fixed-panel epoch audit with UTC snapshot checks, matched changes in task-macro ranking accuracy, task-clustered uncertainty and missingness reporting. **Descriptive only**: time trends cannot prove economics caused improvement.
- `rewardbench/datanet_replay.py`: transparent reproduction of the **published Pod-voting equations only**, including veREPPO lock duration and linear time decay. It does *not* replay the Eval API's final reward.
- [Datanet epoch research protocol](docs/DATANET_EPOCH_PROTOCOL.md) and [one-page engineer export request](docs/ENGINEER_EXPORT_REQUEST.md) define the inputs needed to attempt a faithful economic ablation, respecting privacy and the three-person team's capacity.
- `tools/build_mechanism_demo.py` generates deterministic **simulated** fixtures for unit/CLI validation, clearly unsuitable for scientific claims.

```bash
python tools/build_mechanism_demo.py
python -m rewardbench.longitudinal --tasks examples/study_smoke_tasks.jsonl --scores examples/epoch_simulation_scores.jsonl --split smoke --out runs/demo-only/epoch_report.json
python -m rewardbench.datanet_replay --votes examples/datanet_simulation_votes.jsonl --out runs/demo-only/datanet_votes.jsonl
```

**Still not a publishable research finding:** zero genuine Reppo evaluations, zero independent coding-agent verification logs, zero policy weight updates. A fully replicable demonstration requires real, privacy-cleared exported logs, baseline model responses, and independently test-verified candidate patches. See [current status](results/STATUS.md).

## 2026-11-01 research-facing additions

- `rewardbench/research.py`: **offline** source validation, score ingestion, task-level pairwise accuracy, matched comparisons, coverage and task-clustered bootstrap; refuses duplicate, missing or simulated scores disguised as observed.
- `rewardbench/swebench_import.py`: strict bridge for independently generated coding patches and actual SWE-bench verifier manifests, rejecting candidates without provenance or proof. It does **not** run SWE-bench or provide candidate patches.
- `docs/SWEBENCH_BRIDGE.md`: instructions for a legitimate coding-agent dataset, external test verification, leakage protections and licensing.
- `hf/dataset/`: Hugging Face data card plus **smoke-only** preview JSONL. `hf/space/`: Gradio audit-report viewer with no fabricated leaderboard. Neither is published yet.
- `publication/ABSTRACT_DRAFT.md` and `docs/RESEARCH_RELEASE_GATES.md`: paper draft and falsifiable publication gates.
- **Scientific status: NOT ESTABLISHED.** No real peer scores, independent coding-agent verifications, economic weighting ablation or policy weight updates have been collected.

### Run the offline study engine without any credentials

```bash
python tools/build_study_demo.py
python -m rewardbench.research --tasks examples/study_smoke_tasks.jsonl --scores examples/study_simulated_scores.jsonl --split smoke --out runs/demo-only/audit_report.json
python tools/build_hf_preview.py
```

The example scores are explicitly **simulated** and the demo is for verifying the analysis pipeline, **not a research claim**. Real coding-agent data must follow `docs/SWEBENCH_BRIDGE.md`.

## What is real vs. proposed

- `rewardbench/reppo_adapter.py` implements the **documented** Reppo Evaluation API (`POST /submit` followed by `GET /{evalId}`), including Bearer-key authentication, response parsing, and basic validation.
- `rewardbench/pilot.py` provides a persistent state machine with fail-closed submit attempts, a default non-network preview, 10-candidate example set, max evaluation count, and maximum estimated dollar cap.
- `examples/pilot_cases.jsonl` contains **five simple test tasks with two candidates each**. The answers are self-authored and manually checkable, and one incorrect answer is adversarial. This set is for integration sanity only, **not research-grade evidence**.
- `rewardbench/scoring.py` computes a simple self-consistency baseline and pairwise accuracy; the pilot report also calculates a uniform average of peer scores **only when the API returns them**.
- The actual aggregation weights, incentive exposures, and peer independence are **not yet verifiable through this public API**. Therefore **no causal evidence about economic weighting** can be generated from this scaffold alone.

## Run entirely offline — no API key or spend

Python 3.10+ with only standard-library dependencies:

```sh
python -m unittest discover -s tests -v
python -m rewardbench.cli --input examples/fixture.jsonl --out results/fixture_scores.jsonl
python -m rewardbench.pilot prepare --input examples/pilot_cases.jsonl --run-dir runs/pilot-01 --max-candidates 10 --public-approved
python -m rewardbench.pilot status --run-dir runs/pilot-01
python -m rewardbench.pilot submit-next --run-dir runs/pilot-01 --max-evals 10 --max-spend-usd 2.20
python -m rewardbench.pilot report --run-dir runs/pilot-01
```

`--public-approved` affirms the input content is safe to disclose to Reppo's peer evaluators. It **does not cause a network call**. The default `submit-next` is a preview; the actual network action requires `--live` and an API key.

## Live pilot **only after** explicit approval and secure credentials

1. Sign in at https://eval.reppo.xyz and create a dedicated API key. Put it in your cloud agent/runner's **secret store** under `REPPO_API_KEY` (never commit it, put it in agent prompts, or paste it into a chat).
2. Confirm public visibility, acceptable research data use, account billing, and the precise cost before execution. API docs on 2026-11-01 say **100 credits = $0.01 per settled evaluation**, with 1,000 signup credits; however, the runner conservatively reserves **$0.22 per evaluation** because a higher commercial per-call price was previously discussed. Confirm billing before live use.
3. Follow the offline commands to `prepare` a **new** run directory. Run the following *one at a time*:

```sh
python -m rewardbench.pilot submit-next --run-dir runs/pilot-01 --max-evals 10 --max-spend-usd 2.20 --live
# after the evaluation settles (minimum chosen settlement window = 10 minutes):
python -m rewardbench.pilot poll --run-dir runs/pilot-01 --live
python -m rewardbench.pilot status --run-dir runs/pilot-01
# repeat submit-next/poll until all entries settle, then:
python -m rewardbench.pilot report --run-dir runs/pilot-01
```

**Warnings:** Only one evaluation may be pending per account. Do not blindly retry a failed POST; a response timeout may conceal a successful submission. In that case the state becomes `RECONCILE` and a person must inspect pending evaluations in the dashboard. A `FAILED` evaluation will also remain accounted against the pilot attempt cap. No automatic top-ups, paid loops, or GPU jobs are included. Results live in `runs/`, which is git-ignored. Do not share any live run before a privacy review.

## Plan beyond the API smoke test

**Gate 0 — 10-candidate API sanity:** confirm stable scores, response completeness, charges, privacy, and timestamps. This is not statistical evidence.

**Gate 1 — reward quality:** use 100+ licensed/non-confidential held-out tasks, controlled candidate generation, single-judge and uniform-ensemble baselines, task-clustered confidence intervals. See `docs/PROTOCOL.md`.

**Gate 2 — economic-mechanism ablation:** compare uniform vs economically weighted results *on the same judges' outputs*, only if authentic actual weighting/identity metadata can be exported without violating privacy.

**Gate 3 — learning:** only if prior gates pass and resources permit; make actual policy weight updates and evaluate against a frozen, held-out task suite. DPO-style offline preference tuning is not online RL. No claim of inference-time RL until an online policy-optimization loop is truly run.

## Why a resource-constrained design?

Reppo is a three-person startup with a $500 budget ceiling for this pilot, not a multi-A100 research lab. We minimize first-stage compute while preserving a falsifiable methodology. Any transfer to larger model scales remains an open question.

## References

- Official evaluation API docs: https://docs.reppo.ai/api/eval/overview
- Submit/read contract: https://docs.reppo.ai/api/eval/evaluations
- Peer evaluations: https://docs.reppo.ai/api/eval/peer-assessments
- TTRL original implementation: https://github.com/PRIME-RL/TTRL
- Reppo whitepaper: https://reppo.xyz/Reppo_Whitepaper.pdf
- Official SWE-bench public submission artifacts: https://github.com/SWE-bench/experiments
- Founder-friendly current status: [docs/FOUNDER_STATUS.md](docs/FOUNDER_STATUS.md)

**No third-party paid API calls have been executed by this project in its shipped state. No GPU allocation or spend has occurred.**
