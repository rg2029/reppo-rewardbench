# Agent handoff: Dots / Codex / Work

## Research lead job

Use `README.md`, `AGENTS.md`, `docs/PROTOCOL.md`, and `docs/LIVE_PILOT.md` as governing instructions. Work in this source repository. Preserve protocol and budget gates; be conservative about claims. Before accessing external services, read the API docs. Keep all experiments reproducible and timestamped, with statuses written to `results/STATUS.md`.

## Coding-agent assignment (can start immediately)

1. Run `python -m unittest discover -s tests -v`. Fix bugs and report test count.
2. Validate `python -m rewardbench.pilot prepare ... --public-approved` and run `status`, `submit-next` *without `--live`*, and `report`.
3. Add more mock-transport tests for 401, 402, 409, malformed response, and uncertain POST delivery. Do not hit the live endpoint or insert secrets.
4. Produce a pull request with changed files, tests, and a brief threat model.

## Research-agent assignment (can start immediately)

1. Draft a dataset card and audit licenses for public coding-agent trajectory data.
2. Identify an executable held-out benchmark with deterministic verification, avoiding answer-key contamination and unsafe execution.
3. Create a paired-rank evaluation plan with *task-level* resampling and exploratory confidence intervals. Keep sample size/power limitations explicit.
4. Compare reward methods without confusing uniform averaging, raw peer scores, a Reppo composite, or evidence backed by economic stakes.
5. Publish **nothing** until the founder approves.

## Live pilot operator assignment (blocked by legitimate approvals)

**Requires:** an API key in the cloud environment's secret store; founder acceptance that prompts are publicly visible; the account's true price verified; explicit approval of up to 10 submissions and a conservative $2.20 reserved ceiling.

Follow `docs/LIVE_PILOT.md` and run exactly one `submit-next --live` at a time. Poll only if there is a pending ID. Persist checkpoints; no retry on ambiguous POST. Stop on budget ceiling, malformed responses, or `RECONCILE`. Never expose keys, full peer critiques containing sensitive content, or prompts containing private information.

## Founder review gate

After 10 settled smoke results, deliver: `runs/smoke/report.json`, exact settled/request counts, parse failures, per-account credits used, and whether `peerAssessmentCount` and `evidenceBasis` support moving to a coding benchmark. Say plainly if a real result is not available.

## Start prompt (copy/paste)

> You are the technical lead for Reppo RewardBench. Review AGENTS.md, docs/PROTOCOL.md, docs/API_CONTRACT.md, docs/LIVE_PILOT.md and docs/AGENT_HANDOFF.md. Begin with CPU tests and mock-contract tests. Do not spend money or send live Reppo evaluations until I approve a ten-request cap and secure authentication. Only submit publicly shareable examples. Use checkpointed one-pending-at-a-time execution. Provide reproducible diffs and an honest status report. Our compute budget for the entire project is $500; avoid A100 clusters and do not claim we've demonstrated reinforcement learning without actual policy updates and held-out improvement.
