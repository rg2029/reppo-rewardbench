import argparse
import json
from pathlib import Path
from rewardbench.scoring import majority_scores, pairwise_ranking_accuracy


def run(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = []
    with input_path.open(encoding="utf-8") as src, output_path.open("w", encoding="utf-8") as dst:
        for line_no, line in enumerate(src, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            candidates = obj["candidates"]
            if not candidates or not all("answer" in c and "verified_correct" in c for c in candidates):
                raise ValueError(f"Invalid candidates on line {line_no}")
            scores = majority_scores([c["answer"] for c in candidates])
            outcomes = [c["verified_correct"] for c in candidates]
            record = {
                "task_id": obj["task_id"],
                "fixture_only": True,
                "majority_scores": scores,
                "pairwise_accuracy": pairwise_ranking_accuracy(scores, outcomes),
                "reppo_scores": None,
                "note": "No live Reppo API calls, policy updates or empirical claims."
            }
            dst.write(json.dumps(record) + "\n")
            summary.append(record)
    print(f"Wrote {len(summary)} fixture task results to {output_path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    run(args.input, args.out)

if __name__ == "__main__":
    main()
