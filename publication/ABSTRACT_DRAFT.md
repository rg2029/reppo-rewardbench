# When Is an AI Judge Trustworthy?

**Reppo RewardBench — abstract for the working paper (version 0.2).**  
**Author:** Raghav Rmadya, Reppo Labs

An AI judge can prefer a convincing answer even when the answer fails an executable test or leaves a software system in the wrong state. This paper asks whether economic coordination among evaluators helps distinguish successful agent behavior from failure. We specify a matched comparison of a single language-model judge, a uniformly weighted ensemble, and the complete Reppo Evaluation API across coding, tool use, customer-service trajectories, and research tasks. Each comparison uses candidate outputs with independently checked outcomes; the primary measure is pairwise ranking accuracy at the task level. We also specify a separate within-evaluator replay to test economic weighting, because a service-level advantage cannot establish which component caused it. Two settled arithmetic API evaluations and two engineer-attested voting reports support a limited systems audit: the API operated and displayed vote totals reconciled. They do not establish an accuracy advantage, cross-domain robustness, or an improvement from reinforcement learning. We describe the experimental controls, outcome checks, and reporting requirements needed to investigate those claims.

The manuscript is a working paper. Matched coding-agent, tool-use, service and research benchmark results are not yet included. The protocol is developed by Reppo Labs, which has an interest in the system under evaluation.
