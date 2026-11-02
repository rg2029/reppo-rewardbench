# Four-call coding-agent feasibility pilot: audit (2026-11-02)

**Status: completed; feasibility demonstrated, efficacy not established.** This is an audit of [GitHub Actions run 41372244413](https://github.com/rg2029/reppo-rewardbench/actions/runs/41372244413), not a new evaluation. The run succeeded on its first attempt, from 01:23:30 to 02:20:44 UTC on November 2, 2026. No paid requests were rerun in this audit.

## Frozen source and provenance

The retained artifact `coding-agent-live-results` (artifact ID `13111163207`, 7,858-byte ZIP) contains `frozen_tasks.jsonl`, `reppo/state.json`, and `reppo/report.json`. The frozen source file's independently recomputed SHA-256 matches the state manifest: `5b1d8e29945a8d40b85002053270060ba80991455159a5e880f44693becbf0ee`.

The two frozen tasks are `astropy__astropy-14182` and `django__django-10973`, from `princeton-nlp/SWE-bench_Verified` revision `c104f840cc67f8b6eec6f759ebc8b2693d585d4a`, test split. For all four submitted candidates, the full patch text and instruction match the frozen source exactly, each patch's independently recomputed SHA-256 matches its recorded patch hash, and the correct/incorrect label matches the archived verification metadata. Source records reference original deterministic-test reports and report hashes in S3. **This audit verified the preserved provenance chain, but did not independently fetch or rerun those upstream SWE-bench test reports.** The labels are therefore sourced to frozen external verification rather than newly reproduced here.

## All four settled observations

| Task | Candidate | Frozen test label | Reppo score | Returned equal-weight peer mean | Peer scores |
| --- | --- | ---: | ---: | ---: | --- |
| astropy__astropy-14182 | codex | pass | 60 | 60.00 | 65, 60, 55 |
| astropy__astropy-14182 | haiku | fail | 60 | 65.00 | 65, 65, 65 |
| django__django-10973 | codex | fail | 80 | 83.33 | 85, 85, 80 |
| django__django-10973 | haiku | pass | 75 | 78.33 | 75, 75, 85 |

All four entries have distinct `eval_id` values, `status=SETTLED`, and recorded settlement timestamps. There were no unresolved, failed, pending or missing candidate evaluations (4/4). Each entry records three peer scores, so 12/12 expected peer scores are present. **However, peer model identities vary between candidates**, and the returned uniform peer mean is an *internal* comparison of the same evaluation route, not an independent matched external ensemble. No economic weights or contribution traces were returned; each entry records `cited_pod_count=0` and `evidence_basis=model-judgment`. A causal effect of economic weighting cannot be identified.

## Pairwise outcomes and limitations

For astropy, the Reppo score **ties** the verified pass and fail, worth 0.5 under the frozen tie-half-credit convention; the returned uniform peer means **rank the failing patch higher**, worth 0. For django, Reppo **ranks the failing patch higher**, worth 0; the peer means also rank the failing patch higher, worth 0. Thus task-macro pairwise agreement is **Reppo 0.25 vs internal uniform peer mean 0.00**, a descriptive 0.25 difference across only two task-pairs, not a credible estimate of superiority. The reported majority-vote diagnostic is 0.50, but is also internal. No confidence interval or significance claim is warranted. The model-judge score differences cannot demonstrate improved RL or coding performance.

All four returned `credits_charged=440`, totaling **1,760 credits**. At the workflow's documented $0.0001 per credit this is approximately **$0.176**, but it is a derived conversion, **not independently reconciled billing**. The precommitted conservative spending guard reserved $0.88 at $0.22 per evaluation. There were no additional requests in this review.

## Research interpretation

The study establishes that the Reppo endpoint can accept frozen real coding-agent patches, return settled judgments with per-candidate peer diagnostics, and preserve audit artifacts under a capped, sequential workflow. It does **not** establish better judgment quality, economic aggregation benefit, generalization, or better RL outcomes. A particularly important negative result is that Reppo did not strictly prefer the verified passing patch in either task. These coding results should remain visible as a control domain while the separate, preregistered human-preference/subjective track tests Reppo's hypothesized advantage in ambiguous, nondeterministic judgments.

**Further work:** retain original evidence and no-rerun policy; independently reproduce a subset of external test labels if feasible; pre-register a larger, label-blind holdout; compare against genuinely independent, matched judge baselines; and request auditable economic-weight traces before attributing any performance differences to Reppo's mechanism. Do not promote this two-task result as a benchmark win.
