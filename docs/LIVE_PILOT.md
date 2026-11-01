# Pilot runbook — official Reppo Evaluation API

**Status:** API schema integrated; test fixture integration passed. No authenticated/paid Reppo calls have been made. This runbook is for an authorized operator/agent using a secure environment.

## Official sources verified 2026-11-01

- https://docs.reppo.ai/api/eval/overview — bearer API key, pending limit, credits
- https://docs.reppo.ai/api/eval/evaluations — POST submit, GET by evalId, asynchronous state, response fields
- https://docs.reppo.ai/concepts/evaluation-api — evaluation submissions are public for now

**Critical live constraints:** one pending evaluation per account; minimum API settlement window 10 minutes; API calls return `PENDING` and must be read later; up to three peer assessments; each settled eval listed as 100 credits / **$0.01 in public docs**; free signup allowance 10 evals. A founder previously cited $0.22 per call, so the runner reserves **$0.22 per submission** until the live account rate is confirmed; this is a protective budgeting assumption, not an observed charge. This price may differ from what Reppo bills particular accounts. Confirm pricing and credits in your console before spending. Batching / parallel submits will get `409`.

**Security:** Only send public, authored tasks. The publicly visible submission includes each candidate answer and task context; no keys, private user material, customer traces or hidden benchmark answers. The task's correctness label is never part of the submitted JSON.

## CPU-only setup and smoke test (free)

```bash
python -m unittest discover -s tests -v
python tools/generate_smoke.py
python -m rewardbench.pilot prepare --input examples/pilot_cases.jsonl --run-dir runs/smoke --max-candidates 10 --public-approved
python -m rewardbench.pilot status --run-dir runs/smoke
python -m rewardbench.pilot submit-next --run-dir runs/smoke
```

The last command **previews only**. This pilot is not a scientific experiment: its tasks are intentionally simple and synthetic to validate the live integration and rejection of obvious bad answers.

## When an authorized founder approves API access

1. In `https://eval.reppo.xyz`, create an API key. Store it in Codex/Work/Dots secret settings as `REPPO_API_KEY`. Never paste it into ChatGPT, a command prompt saved in shell history, or Git.
2. Confirm the account's live credit price. Ensure the submission feed is allowed to show these authored prompts.
3. Approve a maximum of **10** submissions for the first run; this is a cap even if free credits exist. No automatic retries.
4. In the secured runtime, use the following commands **one at a time**:

```bash
python -m rewardbench.pilot submit-next --run-dir runs/smoke --live --max-evals 10 --max-spend-usd 2.20
# after the API settlement window closes (at least 10 minutes), run:
python -m rewardbench.pilot poll --run-dir runs/smoke --live
# once SETTLED/FAILED and no longer PENDING, submit-next again
python -m rewardbench.pilot report --run-dir runs/smoke
```

Do not operate a paid monitoring loop without separate approval. A dot may revisit this controlled workflow using its approved scheduled or persistent tasks, but **must** obey the caps and await approvals. After ambiguous submission failures the entry stays `RECONCILE` and cannot be retried automatically, preventing duplicate paid requests.

## What the pilot can and cannot establish

- It can: demonstrate real API interoperability, report parse success, measure scores, compare rankings with deterministic toy correctness, record peer assessment scores and evidence basis, and establish actual billed credits.
- It cannot: establish credible real-world coding reward quality, test model learning, prove economic weighting causes better outcomes, or demonstrate inference-time RL.
- `peerAssessmentCount` does not mean that all judges use independent underlying models; `modelName` is self-reported.
- A numerical average of the same peers (`uniform_peer_mean`) can be compared descriptively with the composite, but it **does not isolate economic weighting**, because the composite may also incorporate datanet evidence and other hidden mechanisms. For a causal ablation the team needs an internal export of the exact aggregation algorithm, weights and peer evidence on matched cases.

## After the smoke test

Review Gate 1; construct 30+ *independently testable, licensed coding tasks*, each with at least one correct and one flawed solution. Run a few candidates to validate domain coverage; inspect `evidence_basis`. Pre-register a held-out set. Only then scale the reward-quality pilot. Deferring training if there is no reliable lift is an intended outcome.
