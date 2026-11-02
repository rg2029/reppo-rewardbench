# Independent fixed-judge natural-prevalence pilot audit (2026-11-02)

**State: PARTIAL, stopped, no automatic retry.** Source: [GitHub Actions run 41438797939](https://github.com/rg2029/reppo-rewardbench/actions/runs/41438797939). The preceding run [41438045214](https://github.com/rg2029/reppo-rewardbench/actions/runs/41438045214) stopped in preflight on an undefined variable **before any model POST**. GitHub Actions offline cohort tests passed in run [41437300750](https://github.com/rg2029/reppo-rewardbench/actions/runs/41437300750); a later offline paid-gate test run 41438642527 also passed. A credentialed read-only model catalog test passed in run [41437514315](https://github.com/rg2029/reppo-rewardbench/actions/runs/41437514315), reporting both model identifiers available.

## Immutable cohort and composition

The 50-pair HelpSteer2 validation preference cohort is frozen at revision `990b2711a36180dd19d9c94b8627844866f8982a`; label-blind input SHA256 `35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39`, private labels SHA256 `76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91`. It has 11 ties, 20 weak, 19 strong among the 50 filtered eligible samples. The prior selected Reppo pilot examples were excluded by source content. Only the **first three predetermined rows** were cleared for the limited HF pilot; the other 47 were **not** transmitted. Neither the full cohort nor the three pilot rows have matched Reppo composite scores.

## Observed fixed-judge results

Score range: 0–100; signed margin is response 2 minus response 1. Human positive strength prefers response 2.

| Natural frozen pair | Human strength | Model | Response 1 | Response 2 | Margin | Human directional alignment |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| 1: physics explanation | −2 | Llama 3.3 70B | 92 | 90 | −2 | Yes |
| 1: physics explanation | −2 | Qwen3 235B | 90 | 45 | −45 | Yes |
| 1: physics explanation | −2 | Uniform external mean | 91 | 67.5 | −23.5 | Yes |
| 2: legal writing | +1 | Llama 3.3 70B | 80 | 90 | +10 | Yes |
| 2: legal writing | +1 | Qwen3 235B | 65 | 95 | +30 | Yes |
| 2: legal writing | +1 | Uniform external mean | 72.5 | 92.5 | +20 | Yes |
| 3: public-figure video introduction | +3 | Llama 3.3 70B | 80 | missing | not computable | not computable |
| 3: public-figure video introduction | +3 | Qwen3 235B | missing | missing | not computable | not computable |

**Completeness:** nine SETTLED POSTs: four for pair 1, four for pair 2 and one Llama score for pair 3. The tenth task, Qwen on pair 3 response 1, was remotely **RESERVED** with attempts=0, but the subsequent push of `SUBMITTING` failed; therefore **no tenth inference POST was made**. The last two proposed tasks were not reached, and no score should be imputed. The 2/2 directional agreements are a highly selected, tiny-n feasibility observation, **not a performance estimate** or statistically meaningful victory.

## Provider usage, reservation and safety

Conservative accounting: $0.50 reserved for each of the 10 remotely recorded entries = **$5.00 reserved** (nine settled + one never submitted), not $5.00 actual billed. Qwen usage contains provider-estimated per-call amounts; Llama records lack invoice-grade USD prices. No invoice reconciliation exists. Combined with $2.64 earlier conservative Reppo reservations and $0.50 uncertain first external call, tracked conservative exposure is **$8.14**; this is not a validated all-project invoice ledger. Founder approved up to $25 additional pilot spend, and the original $500 cumulative ceiling was not raised. The previous ambiguous external request remains excluded from retry.

The run is complete with conclusion **failure** because a GitHub push of the tenth request's `SUBMITTING` checkpoint returned nonzero. The signed no-retry rule worked: the process stopped instead of sending an unlogged POST. Repositories `research_ledger/hf_subjective_50/*.json` contain the nine settled scores and one reservation, no credentials or raw prompt texts. The paid workflow was disabled afterward and `research_controls/hf_subjective_50_gate.json` reset to disabled. **Do not rerun this workflow** or send a duplicate of any of its prior nine settled requests.

## Claims and next scientific interpretation

These nine external scores demonstrate fixed-judge pipeline feasibility and two complete preference alignments. The original **Reppo composite** selected three-pair feasibility result (one tie, two correct rankings) uses *different examples* and cannot be statistically compared with this pilot. The two-task coding-agent result **0.25 task-macro accuracy** remains a negative observation. Neither dataset establishes a generalizable model advantage or any benefit from economic weighting. Economic coordination requires authenticated, same-judgment trace replay with actual production aggregation vs uniform/shuffled economic weights. This is unavailable; do not call the comparison causal.

Paper status: a standalone candid feasibility manuscript is prepared as a **working preprint**, not an arXiv submission. To substantiate superiority or a full 50-pair benchmark, additional explicitly cleared, matched experiments and uncertainty analysis are required.
