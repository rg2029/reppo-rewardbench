# Independent baseline execution blocker audit — 2026-11-02

No paid requests were made during this inspection. Founder has approved **up to $25 additional pilot spend**, not a blanket authorization to rerun existing workflows. Cumulative project cap remains $500.

## Code inspected
- `tools/run_subjective_external_baselines.py`: hard-coded to the **old 3-pair selected pilot**, 12 completions, output `runs/subjective-independent-judges-v1`. It calls `frozen_data` for the earlier stratified selection. It **does not** use the separately frozen natural-prevalence 50-pair cohort. Do not describe a run of this script as a 50-pair evaluation.
- `tools/assemble_human_preference.py`: builds a separate *two-per-stratum* six-pair preflight, not the 50-pair cohort.
- Baseline flow creates a fresh output directory in each Actions job and checks only `GITHUB_RUN_ATTEMPT=1`; this does **not** prevent re-submission of the ambiguous earlier request across a new workflow run.
- Run `41387965762` left 11 entries READY and **1 RECONCILE** after an ambiguous POST; zero settled responses. GitHub artifact `13116550937` contains the checkpoint. Billing screenshot shows November $0.00 usage but does not independently establish non-execution of the POST.
- Existing baseline tests cover parsing, label blindness and caps, but not cross-run duplicate suppression, global spend ledger or exclusion of checkpointed request IDs.

## Required changes before any paid run
1. Materialize immutable frozen **50-pair** manifest and label-blind input artifacts, verify pinned hashes; never change cohort in response to outcomes.
2. Define **new study ID**, separate output and persistent cross-run request ledger keyed by source-content hash, candidate, judge model/revision, rubric hash and request version. Treat prior ambiguous first request as `RECONCILE` and permanently exclude that exact submission from auto-retry; document resulting missingness.
3. Build and test a **read-only** provider model catalog and token-permission check; capture provider/model IDs and exact versions. This cannot be verified from the GitHub secret name alone.
4. Reconcile the possible earlier charge; get model-specific price or conservative worst-case hard cap. The approved $25 is a maximum incremental pilot spend, not sufficient authorization for an unrestricted 50-pair run.
5. Add a persistent global cumulative ledger: earlier Reppo API charges/reservations, Hugging Face uncertain first request, and new reservations. Reject work if either $25 additional or $500 cumulative limit might be crossed.
6. Verify privacy/license clearance row by row; never post uncleared inputs. Report skipped rows rather than swapping in replacements.
7. Score only pre-registered requests with no retries. Preserve attempts, errors, complete/incomplete pairs, actual billed USD and paired confidence intervals. Do not count partial pairs as wins.
8. Separately obtain authenticated same-judgment evaluator traces for the economic-weighting ablation. The baseline comparison alone cannot establish causal benefit of economic coordination.

**Status:** Not execution-ready; engineer's internal-trace export is not a prerequisite for the external baseline, but the above safety/reproducibility controls are.
