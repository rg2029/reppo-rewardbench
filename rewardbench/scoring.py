from collections import Counter
import math
from typing import Optional


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def majority_scores(answers: list[str]) -> list[float]:
    """Self-consistency proxy, *not* economic feedback or an independent judge."""
    if not answers:
        return []
    frequencies = Counter(map(normalize, answers))
    return [frequencies[normalize(a)] / len(answers) for a in answers]


def pairwise_ranking_accuracy(scores: list[float], outcomes: list[int]) -> Optional[float]:
    """Compare only unequal-outcome pairs; ties on score count as half.

    Outcomes must be independently verified binary correctness labels.
    """
    if len(scores) != len(outcomes):
        raise ValueError("scores and outcomes lengths differ")
    if any(type(y) is not int or y not in (0, 1) for y in outcomes):
        raise ValueError("outcomes must be binary integer 0/1")
    if any(isinstance(s, bool) or not isinstance(s, (int, float)) or not math.isfinite(s) for s in scores):
        raise ValueError("scores must be finite numbers, not booleans")
    n = 0
    total = 0.0
    for i in range(len(scores)):
        for j in range(i + 1, len(scores)):
            if outcomes[i] == outcomes[j]:
                continue
            n += 1
            delta = (scores[i] - scores[j]) * (outcomes[i] - outcomes[j])
            total += 1.0 if delta > 0 else 0.5 if delta == 0 else 0.0
    return total / n if n else None
