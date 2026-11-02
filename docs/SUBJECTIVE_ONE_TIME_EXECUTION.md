# One-time subjective feasibility: execution record

Experiment scheduled by GitHub Actions when the workflow is first committed. **Do not rerun it.**
Source: HelpSteer2 `preference/preference.jsonl.gz`, pinned revision `990b2711a36180dd19d9c94b8627844866f8982a`.
Frozen judge-facing SHA256 `7ad782e4a0de979cf55a000ea160c86a6072bf1aa35f09f7afe66f7621c56320`; frozen human-label SHA256 `9621ccae24f5b859f82a02a44b6b35db04afc4ac8f9096a1cf0bd9fa0f71a1be`.

Three public-data examples manually screened for inappropriate confidential details: JavaScript education (human tie), GIS government procurement (weak preference), and carrot/eyesight misinformation (strong preference). The frozen employee-webinar prompt was explicitly excluded. Selection was made before receiving any scores. The three pairs are *not* population representative, and the strong carrot example primarily tests factual reliability rather than open-ended taste.

Two candidate texts per pair, scored **independently** under identical fixed multi-dimensional rubrics. The gold preference label and other candidate do not enter any API request.

At most **six** POST calls, strictly sequential; no parallel calls or HTTP POST retries. Each individual submission is marked SUBMITTING and checkpointed *before* POST. Accepted evaluations are polled by ID. A missing acknowledgement is RECONCILE and immediately stops the workflow; re-running a previously interrupted workflow can double-charge and is prohibited.

Conservative new budget reservation: `6 × $0.22 = $1.32`, against a previously recorded $1.32 reserve and project ceiling $500. Recorded credits and any USD conversion are subject to invoice verification. No unrelated candidate data should be uploaded.

The scored evidence is retained in the run's `subjective-six-call-evidence` artifact. A passing GitHub workflow is **not** evidence of superiority, a deployed economic-weighting ablation, or an RL training experiment. The pilot establishes the mechanics for a larger matched study, followed by external fixed judge baselines and same-judge economic replay when the system makes traces available.
