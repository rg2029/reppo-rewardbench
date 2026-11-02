# Subjective pilot safety review (2026-11-02)

**Status: offline rubric and analysis only; NO paid Reppo calls made.**

## Frozen provenance

Actions run [41379653765](https://github.com/rg2029/reppo-rewardbench/actions/runs/41379653765), artifact `human-preference-preflight` (artifact ID 13112219975, archive digest sha256:8735743134f9846b8e5b9cc4c654cfbd9d0e0738d069a4c5dc99edcb959dd420). NVIDIA HelpSteer2 validation preference revision `990b2711a36180dd19d9c94b8627844866f8982a`. Judge-facing JSONL SHA256 `7ad782e4a0de979cf55a000ea160c86a6072bf1aa35f09f7afe66f7621c56320`; human labels stored separately (SHA256 `9621ccae24f5b859f82a02a44b6b35db04afc4ac8f9096a1cf0bd9fa0f71a1be`). Six pairs: 2 ties, 2 weak, 2 strong. Balanced selection is not population-representative.

## Review and stop conditions

- **Privacy / rights blocker:** one frozen instruction contains a purported internal Cafe24 employee webinar communication, and two include multi-turn assistant/user transcripts. CC BY 4.0 dataset licensing does not itself prove that every underlying prompt can be redistributed to a public-peer API. The public Reppo API documentation warns that peers may see submitted material. Do not submit the frozen set until source-content privacy/third-party rights review and removal/replacement of any restricted rows; replacement would require a NEW predeclared frozen cohort, not silent editing.
- **Idempotency blocker:** documented API POST does not establish a supported idempotency key or a way to recover an accepted but unacknowledged POST. No automated POST retries are permissible. A workflow with six calls must reserve all six calls *before* its first submission and checkpoint each intent before POST; if the POST response is ambiguous, stop immediately. Never rerun the paid workflow.
- **Budget/design:** six pairs require **12 independent candidate evaluations**, not six. A six-evaluation cap permits only three complete pairs, preselected before any scores. Conservative reservation $1.32 (6 x $0.22); founder's $500 total ceiling remains binding across runs. Billing reconciliation pending.
- **Labels and leakage:** the judge-facing JSONL has only `task_id`, `instruction`, `candidates`, and `source`; separate labels include individual annotator strengths. The submission builder sends only the instruction, one candidate answer, and the domain-specific rubric. It does not send source, IDs, counterpart answer, or preference strength. However, original prompt wording and answer length may leak the intended ranking indirectly; inspect each item for such cues. A tied label does not mean objectively identical quality.
- **Analysis:** record absolute score margins for human ties; predeclare an equivalence margin (5 points is a provisional sensitivity threshold, not calibrated); weak versus strong preference agreement separately; individual human disagreement and sample-size limitations. No causal claim about economic weighting from API final scores.

The initial coding feasibility result remains **one tie and one incorrect ranking across two tasks**, task-macro accuracy 0.25 under tie-as-half convention. No subjective scores, comparative baseline, or economic ablation have yet been measured.

## Follow-up

Complete privacy/rights clearance and a recoverable, single-flight, immutable, one-time request ledger with pre-submit reservation and manual recovery rules. Run offline CI before any paid workflow. The current code intentionally cannot submit requests.
