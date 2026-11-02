"""Offline analysis of fixed-judge pair scores against frozen human preferences.

No API requests. Never infer economic causality from independent judge scores.
Input JSON contains IDs, label strengths and per-candidate model scores only.
Missing, invalid or partial pairs remain in denominator and coverage reports.
"""
from __future__ import annotations
from collections import Counter
from math import comb, sqrt
import json


def accuracy(score_1, score_2, strength):
    """Return a non-tie agreement in {0,0.5,1}; ties are separate."""
    if type(strength) is not int or not -3 <= strength <= 3:
        raise ValueError("Invalid human strength")
    if strength == 0:
        return None
    if score_1 is None or score_2 is None:
        return None
    for s in (score_1, score_2):
        if type(s) not in (int, float) or not 0 <= s <= 100:
            raise ValueError("Invalid judge score")
    margin = score_2 - score_1
    if margin == 0:
        return 0.5
    return float((margin > 0) == (strength > 0))


def tie_metrics(a, b):
    if a is None or b is None:
        return None
    if any(type(x) not in (int, float) or not 0 <= x <= 100 for x in (a,b)):
        raise ValueError("Invalid judge score")
    return {"exact_tie": a == b, "within_5": abs(b-a) <= 5,
            "absolute_margin": abs(b-a)}


def summarize(rows, models):
    """One row per frozen pair with {task_id,strength,scores:{model:[a,b]}}.

    'reppo' is another score source, not proof of a causal mechanism.
    """
    if not isinstance(models, list) or not models or len(set(models)) != len(models):
        raise ValueError("Explicit unique models required")
    if len({r["task_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate task IDs")
    out = {"pairs": len(rows), "strength_distribution": dict(Counter(
        "tie" if r["strength"] == 0 else ("weak" if abs(r["strength"]) == 1 else "strong")
        for r in rows)), "models": {}, "paired_primary": None,
        "interpretation": "Composite agreement, not causal economic coordination"}
    for model in models:
        non_tie = []; ties = []; missing = 0; strata = {"weak": [], "strong": []}
        for row in rows:
            pair = row.get("scores", {}).get(model)
            if pair is None or not isinstance(pair, (list, tuple)) or len(pair) != 2 or any(x is None for x in pair):
                missing += 1
                continue
            if row["strength"] == 0:
                ties.append(tie_metrics(*pair))
            else:
                result = accuracy(pair[0], pair[1], row["strength"])
                non_tie.append(result)
                strata["weak" if abs(row["strength"]) == 1 else "strong"].append(result)
        out["models"][model] = {
            "complete_pairs": len(rows) - missing, "missing_pairs": missing,
            "coverage": (len(rows) - missing)/len(rows) if rows else None,
            "non_tie_n": len(non_tie),
            "non_tie_accuracy": sum(non_tie)/len(non_tie) if non_tie else None,
            "weak_n": len(strata["weak"]),
            "weak_accuracy": sum(strata["weak"])/len(strata["weak"]) if strata["weak"] else None,
            "strong_n": len(strata["strong"]),
            "strong_accuracy": sum(strata["strong"])/len(strata["strong"]) if strata["strong"] else None,
            "human_tie_n": len(ties),
            "exact_tie_rate": sum(t["exact_tie"] for t in ties)/len(ties) if ties else None,
            "tie_within_5_rate": sum(t["within_5"] for t in ties)/len(ties) if ties else None,
        }
    if "reppo" in models and len(models)>1:
        control = next(x for x in models if x != "reppo")
        discordance = Counter()
        diffs = []
        for row in rows:
            if row["strength"] == 0:
                continue
            a, b = (row.get("scores", {}).get(x) for x in ("reppo", control))
            if not a or not b or len(a) != 2 or len(b) != 2 or None in a or None in b:
                continue
            ra, rb = accuracy(*a, row["strength"]), accuracy(*b, row["strength"])
            diffs.append(ra-rb)
            discordance[(ra, rb)] += 1
        out["paired_primary"] = {
            "comparison": f"reppo_minus_{control}",
            "matched_non_tie_n": len(diffs),
            "mean_accuracy_delta": sum(diffs)/len(diffs) if diffs else None,
            "paired_outcomes": [{"reppo": k[0], control: k[1], "n": v}
                                for k,v in sorted(discordance.items())],
            "uncertainty_note": "Report exact paired sign/permutation uncertainty at analysis release; do not interpret n=3 or n=50 as powered superiority",
        }
    return out


def main():
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Private score+label analysis JSON (never API input)")
    p.add_argument("--output", required=True, help="Aggregate-only public report")
    p.add_argument("--models", required=True, nargs="+")
    x = p.parse_args()
    rows = json.loads(Path(x.input).read_text(encoding="utf-8"))
    summary = summarize(rows, x.models)
    Path(x.output).write_text(json.dumps(summary, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"pairs": summary["pairs"], "models": x.models, "status": "OFFLINE_ONLY"}))

if __name__ == "__main__":
    main()
