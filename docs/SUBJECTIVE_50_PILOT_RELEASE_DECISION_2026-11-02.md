# Baseline pilot release decision — 2026-11-02

**Scope:** independent Hugging Face fixed-judge pilot only. The first **three** deterministically ordered rows of the existing 50-row HelpSteer2 natural-prevalence frozen cohort are cleared for transmission to the two named independent Inference Providers. The other 47 are NOT approved for paid transmission.

## Concrete audit evidence

- Immutable cohort judge-input SHA256 `35f5d8de7c8f5ee8094ccdda8c1048ddfc78439a07d6bfc71507dd5163735f39` and label SHA256 `76f971f965e2d495730ecaa9880f517012c2709d4da7d5af49c07c4356fc9a91` independently matched artifact `13115862608`, source revision `990b2711a36180dd19d9c94b8627844866f8982a`.
- First three frozen IDs: `helpsteer2-natural-01cd0ea07683341c`, `helpsteer2-natural-033c6fe1c53861e0`, `helpsteer2-natural-05d9f500e3236cbb`. Their prompt/response texts were reviewed for contact data, credentials, nonpublic documents, and obviously sensitive person-level material; no such material was apparent. Prompts concern a physics explanation, a legal writing task, and a public-figure video introduction. This is narrow research transmission clearance, not redistribution of private data or a guarantee that all copyrights have been adjudicated.
- License source: Wang et al., *HelpSteer2-Preference: Complementing Ratings with Preferences*, ICLR 2025; public release CC-BY-4.0. Preserve attribution and do not publish raw source text in GitHub audit.
- Read-only `HF_TOKEN` catalog test `41437514315` succeeded and found both preregistered model IDs with live providers. This only verifies catalog access, not that future paid inference will succeed.

## Prior research-budget reconstruction, deliberately conservative

- Reppo smoke test run `41366113872`: 2 settled calls, reserve **$0.44**.
- Reppo coding-agent run `41372244413`: 4 settled calls, reserve **$0.88**; failed predecessor `41372159595` ended before submission according to logs.
- Reppo subjective run `41387487415`: 6 settled calls, reserve **$1.32**.
- Hugging Face external baseline run `41387965762`: 1 ambiguous first POST, conservatively reserve **$0.50** despite screenshot showing November usage $0.00. No retries.

Total conservative historical exposure recorded in the above runs = **$3.14**. Of this, confirmed API settlement reservation (not invoice spend) is $2.64 and uncertain Hugging Face exposure $0.50. **This is not an invoice reconciliation or an assertion that no other research expenses exist.** Under the separate founder-wide $500 research ceiling, a $6 new pilot reservation yields **$9.14 of tracked exposure**; keep accounting distinct from invoice charges.

## Execution limit

- Approved incremental limit from founder: **$25**; plan is **12 unique external POSTs × $0.50 reserved = $6**.
- All posted requests have a deterministic fingerprint and must be committed to the remote GitHub ledger as `RESERVED` and `SUBMITTING` before POST. Never retry `RECONCILE`, `SETTLED` or prior ambiguous requests.
- The old ambiguous Llama request concerned `helpsteer2-06f9b376120ce1b5`, explicitly excluded from the frozen natural-prevalence selection.
- This pilot does **not** produce a 50-pair benchmark, nor does it test Reppo economic causality. Report all refusals, errors and adverse comparisons. Stop rather than silently substitute models or cleared rows.
