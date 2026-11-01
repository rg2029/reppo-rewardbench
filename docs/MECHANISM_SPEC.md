# Reppo mechanism specification for RewardBench (2026-11-01)

**Purpose:** Make the experimental interventions faithful to the integrated Reppo system. This is a research specification, **not** an independently audited implementation of Reppo's production backend.

## Sources and evidence hierarchy

1. **Founder-confirmed (conversation, November 2026):** Each Eval API request first checks for an existing Datanet signal. Otherwise the network can initiate an evaluation. Primary evaluators are independently operated agent/LLM swarms (optionally with MCP tools) competing for token rewards. Secondary participants lock REPPO for veREPPO voting power and vote for/against primary evaluators, per request or across Datanet epochs. These roles form **one integrated mechanism**, not two different Reppo products. Datanets are domain-specific, continuously refreshed RL feedback environments that may monetize reward signals.
2. **Published whitepaper:** https://reppo.xyz/Reppo_Whitepaper.pdf, sections 4–7: Datanets curate data with token-backed veREPPO voting, time-decayed vote weights, an endogenous/synthetic oracle, and 48-hour epochs. Locking REPPO for veREPPO is explicitly distinguished from stake *slashing* (section 5.3). It specifies data/Pod curation; **it does not by itself fully specify the live Eval API primary-evaluator swarm aggregation**.
3. **Public Evaluation API docs:** https://docs.reppo.ai/api/eval/overview , https://docs.reppo.ai/api/eval/evaluations and https://docs.reppo.ai/concepts/evaluation-api: final score, peer assessments and community-pod evidence; one pending request per account, at least a 10-minute settlement window. `modelName` is self-reported; independently operated nodes need technical provenance to establish model/operator diversity.
4. **Still to verify:** exact per-request aggregation algorithm, weight and incentive fields, whether and how the Datanet signal is reused, confidence calculation, historical snapshots, and relationship between the per-request votes and 48-hour epochs. Production source + redacted traces beat guesses.

## End-to-end request path (logical, not measured timings)

```
Evaluation request (task / candidate / criteria / context)
                 |
     Datanet signal available?
        /                     \
 yes: use as evidence       no: launch/evaluate via primary LLM/agent swarms
        \                     /
         Primary evidence and/or judgments
                         |
         Secondary veREPPO participants vote on evaluators
             (per request; Datanet signal may evolve per epoch)
                         |
             Reppo coordination + aggregation
                         |
              reward score / critique / decision
                         |
           optional downstream use by learning systems
```

**Important:** This schematic is qualitative. It does not assert exactly when voters vote relative to API settlement, how a cache hit is handled, or a specific aggregation formula. Validate against actual immutable logs before depicting it as implementation ground truth.

## Correct evaluation arms

| Arm | Description | Can we run through current public API? |
|---|---|---|
| S | Single fixed LLM judge | Separately, with a judge provider/model |
| U | Fixed independent-judge ensemble, uniform weights | Separately; same prompts and input candidates |
| R | **Complete** Reppo Eval API result (primary + secondary + relevant Datanet evidence) | Yes, opaque full-system output only |
| R-no-economics (internal) | Same primary answers & Datanet evidence, secondary economic effects neutralized *by protocol-owned replay* | **No**; requires authorized source/trace |
| R-shuffled (internal) | Same judgments and Datanet evidence, controlled randomized secondary weights or votes | **No**; requires authorized source/trace |
| R-stale vs R-fresh | Same eligible input under frozen and current Datanet snapshot | **No**, unless snapshots are addressable in the backend |

The original misleading “Reppo primary-only” vs “Reppo secondary-only” product comparison is **removed**. Primary-only is an optional **counterfactual ablation**, not an independently deployable alternative system.

## Unit of evidence and reward paths

- **Per-request path:** independent verified task outcome → matched judge outputs / final Reppo verdict → ranking accuracy, cost, latency, coverage.
- **Datanet path:** a specific Datanet signal state / epoch → scores for a frozen anchor task panel, compared with time-matched baselines; compute *descriptive* trends first.
- **Learning path:** genuinely update model weights using a reward function and test on sealed, unseen tasks; pure selection/best-of-N does not constitute RL.

## Validity threats to pre-register

1. **Label and Datanet contamination:** live public submissions may become visible and may eventually influence Datanet signals. Separate unexposed held-out tasks from repeated probes. Only use repeated probes for descriptive drift diagnostics, not the main efficacy claim.
2. **Judges sharing a base model:** different nodes may be correlated; self-reported names are not proof of independent models.
3. **Economic data != objective truth:** lock duration / amount can affect influence without guaranteeing better assessments.
4. **Temporal comparisons:** a rising accuracy score can reflect changes in tasks, judge models, prompts, participation or data availability. Report contemporaneous baselines and a fixed task panel; causal claims require controlled snapshot replay or randomized assignments.
5. **Cost and latency:** the API's minimum settlement window makes synchronous inference-time gating distinct from cheap offline reward learning.
6. **Slashing claim:** veREPPO locking itself is *not* slashing in the cited whitepaper; do not claim secondary voters get slashed absent production-specific evidence.

## Verification questions for one engineer (once available)

1. For a specific evaluation ID, can we reconstruct the complete primary-judge set, secondary votes and Datanet evidence that contributed to the final reward, without disclosing customer data?
2. What exact weights/parameters apply to veREPPO votes, primary judges, node history, and Datanet signal reuse? Are they deterministic and versioned?
3. Is there a read-only historical snapshot identifier and clear epoch boundary for Datanet signals?
4. Can the same underlying primary judgments be replayed with economic weights set to uniform/zero while preserving everything else?
5. Which hashes can we publish so an external researcher can verify data integrity while private identities remain pseudonymized?

Until answered, present Reppo as **one composite intervention** and record mechanism subcomponents as unverified.
