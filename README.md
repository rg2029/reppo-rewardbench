# Reppo RewardBench

**Can a network of evaluators distinguish an agent that succeeded from one that only sounded convincing?**

A patch may look correct and fail its tests. A tool call may be well-formed but change the wrong record. In both cases an LLM judge could give a favorable score. Reppo RewardBench studies this gap between *judged quality* and *checked outcomes*.

The central comparison is between a fixed single judge, an independently assembled equal-weight ensemble, and the complete [Reppo Evaluation API](https://docs.reppo.ai/api/eval/overview). We rank the same agent outputs against results checked by a task-specific verifier. A second analysis will test whether economic weighting helps, using the same underlying evaluator judgments. The two questions must not be conflated.

[Protocol](docs/PROTOCOL.md) · [Mechanism and open questions](docs/MECHANISM_SPEC.md) · [Public dataset](https://huggingface.co/datasets/Reppo-labs/reppo-rewardbench) · [Report viewer](https://huggingface.co/spaces/Reppo-labs/reppo-rewardbench)

## Evidence at this stage

| Check | Observed | Limit |
| --- | --- | --- |
| Live Eval API smoke test | Two settled evaluations on one arithmetic prompt. The correct answer scored 100/100, the wrong answer 0/100; the peer mean also ranked them correctly. | An integration check, not a comparison of competing judges. |
| Two real voting reports, confirmed by Reppo engineering | Four evaluators, five veREPPO voters per report; all 40 recorded allocations reconcile to the displayed totals. | Original network events have not been independently authenticated. |
| Equal-voter normalization of those reports | Neither report changed its selected evaluator. | These examples do not show an advantage from stake weighting. |

The original voting HTML files remain out of public distribution pending review of their contents and redistribution rights. See the [arithmetic audit](docs/PRIVATE_FIRST_MECHANISM_AUDIT.md), [replay parser](tools/audit_judging_judges.py), and [API smoke result](docs/LIVE_SMOKE_RESULT_2026-11-01.md).

**No matched coding-agent result or reinforcement-learning improvement has been established in this release.** The Hugging Face dataset currently contains ten basic arithmetic *format examples*. They are not benchmark tasks.

## How we'll test it

Each task has two or more real agent-generated outputs and a recorded outcome from an independent checker. For coding, that means executable patch tests. We are also designing tracks for tool-call validity, customer-service state changes, and research tasks with checkable answers. Security stress tests are analyzed separately; each domain keeps its own metric and denominator.

For each candidate we collect:

1. A score from one fixed external LLM judge.
2. Scores from an external, uniformly weighted judge ensemble.
3. The final settled score from the Reppo Evaluation API.

We compare rankings on the **same tasks and candidate presentations**. Task-macro pairwise accuracy is the primary measure; ties count as half a correct ranking. Every release should also show failed requests, missing scores, costs, latencies, and task-level uncertainty. A higher composite score alone would not identify which part of Reppo caused the difference.

Testing *economic weighting* requires a separate replay using the same judges, evidence, and aggregation function, changing only the weights. Testing *learning* requires a separate experiment that actually updates model parameters. We won't describe reranking as reinforcement learning.

## Reproduce the offline checks

Python 3.10+ and the standard library are sufficient for the regression tests and the simulated analysis example.

```bash
python -m unittest discover -s tests -v

python tools/build_study_demo.py
python -m rewardbench.research \
  --tasks examples/study_smoke_tasks.jsonl \
  --scores examples/study_simulated_scores.jsonl \
  --split smoke \
  --out runs/demo-only/report.json
```

The example above is **simulated**. Its scores are not evidence. To audit the voting arithmetic in two permitted HTML reports:

```bash
python tools/audit_judging_judges.py report-1.html report-2.html \
  --output runs/private/vote_audit.json
```

The parser checks displayed allocations; it does not authenticate on-chain events or reconstruct the production reward score. The CPU test workflow makes no paid API calls. Live evaluations run separately with request caps, saved checkpoints, and secure secrets.

[Study inputs](docs/SWEBENCH_BRIDGE.md) · [API contract](docs/API_CONTRACT.md) · [Research release gates](docs/RESEARCH_RELEASE_GATES.md) · [License](LICENSE)

*Reppo Labs develops the system being evaluated. Source code and a passing test suite make the analysis inspectable; they do not constitute independent validation.*
