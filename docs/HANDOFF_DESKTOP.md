# When the founder is at a computer — shortest secure handoff

The assistant has permission to prepare a public research release but has not published a benchmark or initiated paid experiments. The total experimental ceiling is USD $500, not an instruction to spend it.

## Two founder actions

1. In the Reppo Evaluation Console, **revoke the API key previously pasted into chat**. Generate a dedicated new key for the project. In the new private GitHub repository's Settings → Secrets and variables → Actions, create a repository secret named `REPPO_API_KEY`. Never paste it into chat or commit it. If using Codex/Dots instead, set it in their environment's secrets settings. Confirm read/write scope and a budget cap as available.
2. In GitHub, create a private repository `rg2029/reppo-rewardbench`, then import the packaged source ZIP. (GitHub app currently offers repository editing but not repository creation.) Authenticate Hugging Face separately when ready. Do not make the repository public before the independent-outcome audit and release gates.

## Technical agent actions immediately afterward

Run tests; read `docs/RESEARCH_RELEASE_GATES.md`; verify documented current Reppo API costs, submission visibility, and policy; run **one** public smoke submission under a $0.22 conservative reserved cap; wait for settlement then poll, log actual credit charge and method coverage. On a clean settlement, complete at most 10 smoke submissions; no automatic recharge or unattended paid loop. Then source the licensed verified coding tasks and independent model-generated candidate patches. Economic weighting data export needs exact weights and provenance, not only average peer scores.

## No need for large GPU up front

Use CPU and existing verifiable coding-agent patches for reward-quality gates. Reserve any GPU spend for matched weight-update experiments only after reward scores are reliable. A GPUless reward study is **not** inference-time RL.
