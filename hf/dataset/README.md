---
language:
- en
license: cc-by-4.0
pretty_name: Reppo RewardBench - API Format Examples
task_categories:
- text-classification
tags:
- reward-modeling
- evaluation
- smoke-test
size_categories:
- n<1K
---
# Reppo RewardBench: API format examples

This small dataset is for checking parsers and evaluation requests. **It is not a benchmark result.** The separate first two-task coding-agent feasibility run is [documented in GitHub](https://github.com/rg2029/reppo-rewardbench/blob/main/results/CODING_AGENT_FEASIBILITY_2026-11-02.md); these ten arithmetic examples are not its inputs.

The file `data/smoke_preview.jsonl` has ten candidate answers drawn from five basic arithmetic questions, including one attempt to redirect an evaluator through the candidate text. The correctness fields were written for this fixture. They are not labels from an independent execution harness; the candidate answers are not coding-agent trajectories.

## What it can be used for

Load the JSONL file to check schema handling, scoring code and prompt-injection hygiene:

```python
from datasets import load_dataset
ds = load_dataset("json", data_files="data/smoke_preview.jsonl", split="train")
```

The [GitHub repository](https://github.com/rg2029/reppo-rewardbench) contains the evaluation protocol and offline scoring code. The [Space](https://huggingface.co/spaces/Reppo-labs/reppo-rewardbench) is a local JSON report viewer; it does not run experiments.

## What the study will require

Real, model-generated candidate outputs; independent verifier outcomes; pinned source versions and task IDs; allowed redistribution; and scores from the same fixed comparison methods. Coding patches, tool calls, and longer agent traces need different outcome checkers. A combined analysis must preserve those distinctions. We will publish per-task coverage and failures, not just aggregate accuracy.

Do not submit customer data, private code, credentials, hidden tests, or answer keys to a public evaluation API. Code candidates should only be executed in isolated test harnesses.

## License

The ten authored format examples are released under CC BY 4.0. That license does not apply to external benchmark tasks, model outputs, or third-party repositories. Any subsequent real dataset release needs its own rights review.
