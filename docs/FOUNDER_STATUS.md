# Founder-facing status (2026-11-01)

**We are building a reproducible research benchmark, not a marketing leaderboard.**

### Ready now

- Offline benchmark scoring and uncertainty analysis.
- Asynchronous, sequential Eval API client and 10-candidate smoke pilot (mock-tested, **not used live**).
- Strict SWE-bench candidate provenance importer (does not itself generate patches or run a Docker verifier).
- New mechanism-specific protocol and descriptive cross-epoch audit CLI.
- Hugging Face **draft** data card and demo Space (not published).

### Not ready yet

- 100+ actual coding-agent tasks with license-cleared, independently executed outcome-verification logs.
- Third-party single judge / model ensemble responses at fixed model versions.
- Complete Reppo peer/economic dataset and production aggregation replay; internal export request drafted.
- Live Reppo API responses after secure key rotation.
- Learned policy checkpoint / genuine reinforcement learning experiment.
- External researcher replication / scientific claims / paper submission.

### What requires founder or engineer input

1. On desktop: create private `reppo-rewardbench` GitHub repo, grant automation access; choose a Hugging Face organization. No TinyFish required if manual account creation is simpler.
2. Rotate the API key posted in chat, securely store the replacement as `REPPO_API_KEY`; never paste it into messages or source code.
3. One engineer: review the **one-page export request** (`docs/ENGINEER_EXPORT_REQUEST.md`) and supply an anonymized internal protocol trace plus historical Datanet snapshots where possible.
4. Human technical reviewer: confirm public dataset licensing, benchmark leakage protections and results before publishing.

**Budget:** Approved ceiling USD $500. **Recorded live spending so far: $0.** The existing local run outputs are simulations/mocks only. Any future costs must be logged against the ceiling. A three-person startup should not be asked to rent an eight-A100 cluster just to validate reward quality.