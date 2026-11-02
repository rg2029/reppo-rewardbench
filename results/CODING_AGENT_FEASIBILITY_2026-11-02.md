# Coding-agent feasibility pilot: two archived SWE-bench tasks

**Run:** [GitHub Actions #41372244413](https://github.com/rg2029/reppo-rewardbench/actions/runs/41372244413) (completed successfully 2026-11-02 02:20 UTC).  
**Evidence:** saved `coding-agent-live-results` ZIP artifact (run artifact ID `13111163207`), containing the frozen input, per-submission state and generated report.  
**Scope:** four live Reppo Evaluation API submissions, two coding tasks, two authentic model-generated patches per task. **Exploratory feasibility only; not a test of improved RL or economic voting.**

## Raw observations

| Upstream task ID | Codex archived verifier | Haiku archived verifier | Reppo Codex score | Reppo Haiku score | Reppo ranking | Reppo peer mean Codex / Haiku |
| --- | --- | --- | ---: | ---: | --- | --- |
| `astropy__astropy-14182` | PASS | FAIL | 60 | 60 | Tie | 60 / 65 |
| `django__django-10973` | FAIL | PASS | 80 | 75 | Incorrect | 83.33 / 78.33 |

**Scoring rule:** pairwise ranking accuracy is 1 for the higher score on the upstream verifier-passing patch, 0 for the higher score on the verifier-failing patch, and 0.5 for a tie. The task-macro Reppo score is **0.25** (0.5, 0.0). A simple average of the peers returned *by Reppo* scores **0.0** (0, 0) on these two tasks; this is **not** an independent, fixed external ensemble. The repo's deterministic majority/self-consistency placeholder scores 0.5 on each task, but is **not** a meaningful external LLM judge baseline.

## API execution and cost

All four submissions returned `SETTLED`. No recorded `FAILED`, `RECONCILE`, or pending entries remained. Each evaluation reported 440 credits charged; total **1,760 credits**. At the rate in the pilot report, this would be **$0.176**, not a verified invoice. The explicitly capped budget reserve was $0.88; no evidence of exceeding it. Each response reported three peer assessments. The peer model name fields are self-reported and varied between evaluations. The observed `evidence_basis` field was `model-judgment`, and `cited_pod_count` was zero in all four responses. Neither field verifies whether an economic voting mechanism participated behind the scenes.

## Ground truth and sample construction

The tasks were selected before Reppo scores were collected, by sorting publicly archived SWE-bench Verified task IDs and requiring two distinct patches from Codex and Haiku with **discordant upstream verifier outcomes**; only two pairs were submitted in this pilot. All four verifier labels and report hashes are retained in the frozen source manifest. This analysis relies on **archived third-party SWE-bench harness reports**; the tests have **not been independently rerun by Reppo**.

- Dataset revision: `princeton-nlp/SWE-bench_Verified`, SHA `c104f840cc67f8b6eec6f759ebc8b2693d585d4a`.
- Frozen two-task inputs ZIP member `frozen_tasks.jsonl`, SHA256 `5b1d8e29945a8d40b85002053270060ba80991455159a5e880f44693becbf0ee`.
- Source archive: public `swe-bench-submissions` object storage; archived runs `20260219_mini-v2.0.0_gpt-5-2-codex` and `20260217_mini-v2.0.0_claude-4-5-haiku-high`.
- Four evaluation IDs, exact settlement timestamps, source patch hashes and archived verifier report SHA256 hashes appear in the saved artifact. Avoid editing this evidence.

## Interpretation and next experiment

The API handled real coding patches and returned settled scores. On this tiny, deliberately selected pass/fail sample, **it did not consistently rank correct patches above incorrect patches**. This finding must not be framed as a system-wide failure or success: n=2 tasks, labels were not reverified in an independent harness, and no external single-judge or fixed-judge-ensemble controls were run.

Next: audit the verifier reports and any judge-visible patch truncation; add a task-level random sample with natural success/failure prevalence and prespecified thresholds; evaluate matched **external fixed judges** with the same prompts; log peer/judge coverage, latency, and abstentions; and only then expand the sample. The effect of veREPPO weighting cannot be identified without a faithful same-judgments replay of the production aggregation. Nothing in this pilot involves policy weight updates.
