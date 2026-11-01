# Reppo Eval API contract — verified against public documentation on 2026-11-01

Official docs: https://docs.reppo.ai/api/eval/evaluations and https://docs.reppo.ai/api/eval/overview

- Root: `https://eval.reppo.xyz/api/v1/agents/eval-requests`
- Authentication: `Authorization: Bearer <REPPO_API_KEY>`.
- Submit: `POST /submit` with JSON `{type: "answer", payload: string, criteria: string[], context: string, settlementMinutes: 10}`. Accepted values for `settlementMinutes`: 10, 15, 30, 60, 120, 360, 720, 1440. Response: `201 {evalId, id, status:"PENDING"}`.
- Read: `GET /{evalId}`. Status is `PENDING`, `SETTLED`, or `FAILED`; `result.verdict.score` is 0–100. Optional `peerAssessmentCount`, `peerAssessments[].score`, `result.evidence`, `result.verdicts[]`, `creditsCharged`.
- `payload` max 50 KB; `context` max 32 KB; at most 10 criteria of 2 KB each.
- Only **one PENDING evaluation per account**; settling may occur after the chosen minimum 10-minute window, rather than instantaneously.
- Published billing: 100 credits per settled evaluation, at a claimed price of $0.01; check billing dashboard in case pricing changes. Sign-up bonus is described as 1,000 credits.
- Peer evaluations may contain full pending submissions from other accounts. Treat all test tasks and candidates as **publicly observable**, never put proprietary code or private data in them. Peer model names are self-reported and cannot prove independence.
- Aggregation is not documented as an equal-weight mean and is not necessarily equivalent to its peer-only mean. Do not infer token incentives or economic contribution from `peerAssessments[]` alone.

## Supported integration

`ReppoAdapter.submit()` posts one evaluation; `ReppoAdapter.get(evalId)` reads it. `summarize_settlement()` extracts final score, peer scores (if present), confidence, evidence basis, and credits while omitting full payloads and critiques from exported analysis.

The mock tests verify path, schema, no ground-truth leakage, payload caps, error states, and resumption logic. Live API authentication has **not** been exercised.

## Not yet known / product-team clarification

- Whether there are sufficient independent peers for each evaluation under the current network load.
- How economic stake, aggregation weights, history and reviewer reputation contribute to the final score; need genuine weight snapshots for H2.
- Whether fine-grained rubric feedback is sufficiently stable for RL reward shaping; how model-judgment vs community-pod verdicts vary.
- Whether candidate submissions/results can be publicly released under API terms and privacy restrictions.
- How API rate limits and account charges behave in production beyond the documented one-pending limit.

**Do not interpret absent peer scores as zero.** The pilot reports uniform mean only for returned peer judgments and separately reports missingness.
