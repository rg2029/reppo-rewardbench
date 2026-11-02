# Working on RewardBench

Reppo RewardBench tests whether the complete Reppo reward signal predicts independently
verified coding-agent outcomes better than fixed, conventional judges.

Before changing analysis code, read [README](README.md), [protocol](docs/PROTOCOL.md),
[API contract](docs/API_CONTRACT.md) and [release gates](docs/RESEARCH_RELEASE_GATES.md).
Run `python -m unittest discover -s tests -v` before merging changes.

## Evidence rules

- Keep real results, archived verifier reports, proxy calculations and simulated
  fixtures clearly separated. Never label a fixture or smoke test as benchmark evidence.
- Compare methods on the *same* tasks/candidates. Preserve missing responses,
  tie counts, exact denominators, prompt/model versions and task-level uncertainty.
- Do not attribute differences to economics without a same-judgments, same-evidence
  replay that changes only the economic weighting.
- Reward ranking, best-of-N selection, offline preference training, and true
  online reinforcement learning are different experiments.
- Record upstream data revision, verifier artifact hashes, candidate source and
  licensing. Do not leak gold patches, hidden tests or correctness labels in API requests.
- No untrusted candidate code may execute outside an isolated test harness.

## Operational rules

- Store credentials only in environment secrets. Never write tokens to source,
  logs, benchmark examples or pull-request discussions.
- Paid API submissions must require explicit cost and count limits; no recurring
  paid loops or automatic top-ups. One Reppo request may be pending at a time.
- Never retry ambiguous POSTs. A failed or interrupted run must retain its
  checkpoint and stop for reconciliation.
- Review public-data rights, privacy and claims before publishing results.
- Favor small, auditable changes over additional infrastructure.

Current experimental status is recorded in [results/STATUS.md](results/STATUS.md).
