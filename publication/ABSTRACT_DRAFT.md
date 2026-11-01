# Reppo RewardBench: Can Independent Economic Feedback Improve Reinforcement Learning?

**Status: Protocol / abstract draft. No experiments reported.**

## Abstract — prospective, not a results summary

AI systems increasingly use evaluations to select outputs, assign credit to agent actions, and update policies. Yet reward signals can be noisy, correlated, gamed or misaligned with independently verifiable outcomes. We propose RewardBench, an openly reproducible evaluation protocol measuring whether independent, economically coordinated feedback can improve reward accuracy and downstream learning for coding agents. Our protocol compares single-judge scores, uniform aggregates of independently generated assessments, and the Reppo network's composite verdict, with a separate within-assessor ablation of economic weighting where exact stake and aggregation records are accessible. We preregister task-level splits and matched outcome verification, measure accuracy and uncertainty using task-clustered resampling, and distinguish best-of-N selection from offline preference training and true online RL. We design for limited compute and publish negative or inconclusive results as well as any positive findings. **No empirical results or reinforcement-learning claims are made in this draft.**

## Required sections before preprint submission

1. Related work: RewardBench 2, TTRL, ThetaEvolve, credit assignment, verifier hacking.
2. Dataset selection, licenses, provenance, exact train/validation/test partition, source code hashes.
3. Candidate generation with frozen model versions, sampling seeds, and deterministic execution evidence.
4. Baselines and controlled economic-weight ablations.
5. Mean task-level accuracy, confidence intervals, robustness attacks, error analysis and cost/latency.
6. Policy learning (if run): training curves, held-out results, matched compute, seeds, reproducible checkpoints.
7. Threats to validity, disclosure of Reppo authorship, compute constraints and negative outcomes.
8. Independent reproduction instructions and artifacts.
