# Reppo RewardBench

**Can economically coordinated evaluators produce better reward signals for coding agents than conventional LLM judges?**

Reppo RewardBench is an open research project from Reppo Labs. We are testing a specific claim, not assuming it: when model outputs are judged by multiple evaluators whose influence is shaped by economic feedback, do the resulting rewards better predict independently verified success?

The immediate outcome is **reward-ranking accuracy**. Whether those rewards actually improve model learning is a separate, later experiment.

[Research protocol](docs/PROTOCOL.md) · [Current results](docs/LIVE_SMOKE_RESULT_2026-11-01.md) · [Mechanism](docs/MECHANISM_SPEC.md) · [Dataset](https://huggingface.co/datasets/Reppo-labs/reppo-rewardbench) · [Interactive viewer](https://huggingface.co/spaces/Reppo-labs/reppo-rewardbench)

## What we know so far

| Evidence | Observation | What it does not show |
| --- | --- | --- |
| Live Eval API smoke test, 1 arithmetic task / 2 submissions | Correct answer scored **100/100**; incorrect answer **0/100**. Both settled. Equal-weight peer scores also ranked them correctly. | Any advantage over a conventional judge; coding-agent performance; RL improvement. |
| Two engineer-attested real evaluation reports (October 29, 2026) | Four primary evaluators and five veREPPO voters per report. **40/40 allocations** reconcile to the displayed voting totals. | Independent verification of network events or whether the economic votes improve judgment quality. |
| A simple one-voter-one-vote normalization of those two reports | **Same selected evaluator** as the recorded stake-weighted totals in both cases. | A benefit or failure of economic weighting in general. Two cases are not a benchmark. |

The two original report HTML files are not redistributed here pending review of their publication rights. [Audit method and limitations](docs/PRIVATE_FIRST_MECHANISM_AUDIT.md) · [Read-only parser](tools/audit_judging_judges.py). Reppo engineering confirmed that the reports are real, but their event-level provenance has not been independently authenticated.

**There are no independently test-verified coding-agent results in this release. There has been no model training or inference-time RL experiment.** The current Hugging Face dataset is a small, authored integration fixture, not an evaluation leaderboard.

## The experiment

We will use a frozen set of coding tasks, each with at least one passing and one failing candidate patch. Candidate outcomes must come from a real, independently run test harness—not an LLM's opinion of whether the code looks right.

Each candidate will be evaluated under three matched conditions:

1. **Single judge:** one fixed LLM, prompt and scoring rubric.
2. **Uniform ensemble:** multiple fixed judges, with equal aggregation.
3. **Reppo:** the complete Eval API result, including its primary evaluators, secondary veREPPO feedback and any applicable Datanet signal.

The primary metric is **task-macro pairwise ranking accuracy**: how often a method ranks the verified passing candidate above the failing candidate, averaged across tasks. We report ties, missing results, costs, task-level uncertainty and every failed evaluation. All comparisons use the same tasks and candidate outputs.

A Reppo-versus-ensemble difference **cannot by itself establish that economic weighting caused the difference**. That requires a separate same-judgments replay, with the actual aggregation inputs and economic weights held or changed under explicit controls. See [protocol](docs/PROTOCOL.md) and [data needed for the replay](docs/ENGINEER_EXPORT_REQUEST.md).

## Run the tools

The offline code uses Python 3.10+ and the standard library. No API key, GPU or paid model is needed to run the tests.

```bash
python -m unittest discover -s tests -v

# Build and score a clearly simulated study, to check the analysis pipeline.
python tools/build_study_demo.py
python -m rewardbench.research \
  --tasks examples/study_smoke_tasks.jsonl \
  --scores examples/study_simulated_scores.jsonl \
  --split smoke \
  --out runs/demo-only/report.json
```

The command above produces **synthetic data only**. Do not quote its scores as findings.

To check the vote arithmetic in any approved `Judging Judges Report` HTML exports:

```bash
python tools/audit_judging_judges.py report-1.html report-2.html \
  --output runs/private/vote_audit.json
```

That parser checks the report's displayed numbers. It does not query the blockchain or validate the final reward computation.

For real scoring, start with [the study input format](docs/SWEBENCH_BRIDGE.md), [API contract](docs/API_CONTRACT.md) and [checkpointed pilot runner](rewardbench/pilot.py). The API is asynchronous; never retry an ambiguous submission blindly or put keys in source files. **No paid calls run in CI.**

## Repository map

- `rewardbench/`: API adapter, dataset checks, scoring, matched comparisons, bootstrap statistics and limited vote-replay tools.
- `tests/`: CPU-only regression tests, run by [GitHub Actions](.github/workflows/cpu-tests.yml).
- `docs/PROTOCOL.md`: study design, controls, endpoints and limits.
- `docs/MECHANISM_SPEC.md`: what is documented about Reppo's integrated mechanism, and what remains unverified.
- `docs/PRIVATE_FIRST_MECHANISM_AUDIT.md`: two real, engineer-attested case reports, their arithmetic checks and limits.
- `hf/`: public Hugging Face dataset preview and static report viewer. No private traces are included.

## What would count as a meaningful result?

The next milestone is a small set of **independently verified coding-agent candidates** scored by all three methods, with the raw task provenance and matched comparison available for scrutiny. After that: a larger sealed holdout, a faithful economic-weighting ablation, and—only if justified—a separate learning experiment with actual model updates.

The study protocol includes null results, failure modes and the data needed to reproduce each comparison.

[Release gates and limitations](docs/RESEARCH_RELEASE_GATES.md) · [Live API smoke-test record](docs/LIVE_SMOKE_RESULT_2026-11-01.md) · [License](LICENSE)
