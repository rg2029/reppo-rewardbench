"""Transparent task-cluster bootstrap for exploratory matched-reward comparison."""
import math
import random
from typing import Optional


def paired_bootstrap_delta(pairs: list[tuple[float, float]], *,
                           seed: int = 20261101, draws: int = 2000) -> Optional[dict]:
    """(method A, method B) task-mean paired accuracy, with 95% bootstrap interval.

    This is uncertainty quantification, NOT a significance or generalization guarantee.
    Conditions must share tasks and independently labeled reference outcomes.
    """
    if len(pairs) < 2:
        return None
    if draws < 100:
        raise ValueError("At least 100 bootstrap draws required")
    if any(isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or not math.isfinite(a) or not math.isfinite(b) or not (0 <= a <= 1 and 0 <= b <= 1) for a, b in pairs):
        raise ValueError("Accuracy pairs must be bounded numeric values")
    rng = random.Random(seed)
    n = len(pairs)
    values = []
    for _ in range(draws):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        values.append(sum(a - b for a,b in sample) / n)
    values.sort()
    observed = sum(a - b for a,b in pairs) / n
    return {"n_tasks": n, "delta_mean": round(observed, 4),
            "bootstrap_95_ci": [round(values[int(0.025 * draws)], 4),
                                round(values[min(draws - 1, int(0.975 * draws))], 4)],
            "bootstrap_draws": draws, "seed": seed, "exploratory_only": True}
