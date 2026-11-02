# Live API gate: two-evaluation smoke result (2026-11-01)

**Status:** Reppo Eval API submission and settlement succeeded. This is an **integration smoke test**, not evidence that economic voting improves reward quality or learning.

- [GitHub Actions execution log and private artifact](https://github.com/rg2029/reppo-rewardbench/actions/runs/41366113872) — completed successfully.
- One arithmetic task (pilot_01): compute 17 + 26.
- Correct candidate 43: Reppo final score **100/100**, settled.
- Incorrect candidate 42: Reppo final score **0/100**, settled.
- One complete paired task; two settled evaluations; zero failed or pending.
- On this one task, Reppo task-macro pairwise ranking accuracy **1.0**, equal-weight peer mean **1.0**, and a simple majority/self-consistency comparator **0.5**. Sample size is too small for scientific generalization or significance intervals.
- The API reported **880 total credits charged**. Script's documented-rate estimate is $0.088; actual account billing needs independent confirmation. The conservative reservation was $0.44; **do not present the dollar estimate as a verified invoice**.
- **No RL training, policy updates, coding-agent test outcomes, or controlled economic-weighting ablation** occurred.
- Sequential asynchronous settlement took roughly 30 minutes for both candidates. Do not retry uncertain POST requests.

## Next gate
Freeze 5–10 fresh or licensed coding-agent task/candidate pairs with independently executed test logs and model provenance; compare fixed single judge, uniform peers and full Reppo. Report failures, coverage, null findings, costs, and methodological limitations.

The separate two HTML example reports are arithmetic-audited but **not authenticated** as real network execution: see [Private mechanism audit](PRIVATE_FIRST_MECHANISM_AUDIT.md).
