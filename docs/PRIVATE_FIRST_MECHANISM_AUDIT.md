# Reppo RewardBench: first mechanism trace arithmetic audit

Status: **engineer-attested real Reppo reports, privately audited for arithmetic consistency; not independently authenticated.**

The two supplied October 29, 2026 "Judging Judges Report" HTML exports were independently parsed with Python's standard library. The importer verifies:

- Each secondary node holder's **absolute** allocation amounts sum to their declared veREPPO balance (important when negative allocations occur).
- Per-evaluator **signed** allocations sum to the displayed final veREPPO net totals.
- The displayed winner has the maximum reported signed net balance.
- A hypothetical equal-influence-per-voter comparison: divide each node's signed allocations by that node's veREPPO balance, then aggregate normalized scores across node holders.

## Observations

| Metric | Bitcoin price-by-end-2026 report | Dune 3 report |
|---|---:|---:|
| Primary evaluators | 4 | 4 |
| Secondary node holders | 5 | 5 |
| Signed allocations | 20 | 20 |
| Negative allocations | 0 | 2 |
| Total veREPPO held | 5,800 | 5,800 |
| Total **absolute** allocation magnitude | 5,800 | 5,800 |
| Total **signed** net allocation | +5,800 | +4,980 |
| Reconstructed totals match the report | Yes | Yes |
| Reported winner | evaluator-4 | evaluator-1 |
| Equal-influence-per-voter winner | evaluator-4 | evaluator-1 |

## Interpretation

This shows the *displayed report* is arithmetically consistent in these two instances. Reppo engineering has confirmed that both reports represent real evaluations. This does not independently authenticate event provenance or demonstrate improved reward accuracy. Neither report contains an independently verifiable correct/incorrect outcome for a code patch. Both voter-normalization schemes pick the same displayed winner; neither example shows an economic weighting benefit.

The final verdict is produced by a separately named model in the reports; do not treat the maximum vote as proof that the production Eval API score is determined by the same arithmetic. Dates are report generation timestamps, not proof of vote settlement or independence.

## Provenance and publication

Reppo engineering confirms both reports are real. The original HTML reports remain private until Reppo explicitly confirms they may be redistributed without exposing any private customer or evaluator information. No source HTML is included in GitHub automatically. No secrets or paid API usage are required to run the parser.

## Reproduce locally

```bash
python tools/audit_judging_judges.py test-case-01.html test-case-02.html --output replay_audit_private.json
```

The resulting file contains report questions, model identifiers, allocations and SHA256 hashes for provenance. Do not add it to public repositories without a review.