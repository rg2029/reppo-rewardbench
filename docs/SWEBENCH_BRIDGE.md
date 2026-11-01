# Verified coding-agent task pipeline (engineering specification)

## Why SWE-bench?

Use the official benchmark's real GitHub issue prompts and test harness rather than fabricating an unverified coding-agent dataset. The [SWE-bench Verified dataset](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) has 500 expert-vetted issues. The [SWE-bench harness](https://github.com/SWE-bench/SWE-bench) verifies candidate patches in Docker. The harness documentation recommends >=120 GB available storage, >=16 GB RAM and >=8 CPU cores; this cannot be assumed on a phone or basic HF Space. Our local tests never execute untrusted patches.

## Source-locked data flow

1. Pin the public dataset repo revision and record its terms, source repository commits, `instance_id`, task statement and relevant licenses. The full verified dataset is a benchmark test set; do not train on it or call a locally chosen portion an official benchmark score.
2. Obtain two or more **independently model-generated** patches per selected issue, using a versioned coding agent. Preserve model and generation configuration. Do NOT use gold patches as candidates for the scientific comparison.
3. Run every candidate through the **official SWE-bench harness in isolated containers**, preserving raw logs, run IDs, task versions, test outcomes and SHA256 hashes. Ambiguous/harness-failing cases require human review and must be disclosed.
4. Normalize to the strict three-manifest import schema below; create a task-level matched pass/fail pair. The public API submission must include the task statement and candidate patch only, never gold/test patches or hidden verifier verdicts.
5. Freeze the exact task/candidate manifest and SHA before scoring with Reppo or other reward methods. The published dataset should identify upstream dataset revision and log hashes; redistribute material only when compatible with third-party licenses.

## Input manifests (JSONL)

**tasks.jsonl**: one record with `instance_id`, `repo`, `base_commit`, `dataset_revision`, `license`, `problem_statement` per task.

**candidates.jsonl**: `instance_id`, `candidate_id`, `model_patch`, `origin: "model_generated"`, `model_id`, `generation_config_sha256`. This is **not** automatically produced by the official SWE-bench dataset; you must run or obtain authentic generated patches.

**verifications.jsonl**: `instance_id`, `candidate_id`, `resolved: true|false`, `harness_run_id`, `log_sha256` (raw verifier run artifact). This is a **normalized audit manifest** built from the official harness logs, not a claimed native output schema.

## Convert into the RewardBench research manifest

```bash
python -m rewardbench.swebench_import \
  --tasks tasks.jsonl --candidates candidates.jsonl \
  --verifications verifications.jsonl \
  --out runs/study/verified_tasks.jsonl --audit-out runs/study/import_audit.json
python -m rewardbench.research --tasks runs/study/verified_tasks.jsonl --strict
```

The conversion excludes tasks without both a passing and failing independently verified candidate and **records each exclusion** in its audit. It refuses missing verification, ambiguous labels, duplicate task IDs or unproven candidate provenance.

## Labels, comparative data and cost discipline

Generate a score row for each `{method,task_id,candidate_id}` with numeric score 0–100 and `source: "observed"`. The comparison CLI requires complete candidates per task and reports coverage and missingness. Do not include pretend scores in the scientific score file.

Actual Reppo API results require sequential submit/poll with a >=10-minute settlement and at most one pending request per account. At 200 candidates, the minimum serial settlement window alone is 2,000 minutes, excluding processing overhead; this is a practical bottleneck. Arrange sanctioned parallel evaluator accounts or asynchronous collection **without** evading service limits, or reduce candidate sample size for the first feasibility study.

`SWE-bench Verified` is a well-recognized benchmark, but the combined RewardBench experiment must be labeled clearly as an independent reward study, not as official SWE-bench leaderboard performance until the official scoring rules and submission process are met.
