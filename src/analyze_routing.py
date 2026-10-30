import argparse
import json
from pathlib import Path

import pandas as pd

from src.routing import route_prediction


def analyze_routing(predictions: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    decisions = predictions.apply(
        lambda row: route_prediction(
            row["predicted_label"],
            float(row["predicted_confidence"]),
        ),
        axis=1,
    )
    routed = predictions.copy()
    routed["routing_action"] = [decision.action for decision in decisions]
    routed["routing_reason"] = [decision.reason for decision in decisions]

    action_counts = routed["routing_action"].value_counts().to_dict()
    total = len(routed)
    summary = {
        "sample_size": total,
        "action_counts": action_counts,
        "action_rates": {
            action: count / total for action, count in action_counts.items()
        },
        "human_review_rate": (
            routed["routing_action"] == "HUMAN_REVIEW"
        ).mean(),
        "monitor_rate": (routed["routing_action"] == "MONITOR").mean(),
        "automated_action_rate": (
            routed["routing_action"] == "AUTOMATED_ACTION"
        ).mean(),
        "pass_rate": (routed["routing_action"] == "PASS").mean(),
    }
    return routed, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    args = parser.parse_args()

    predictions = pd.read_csv(args.predictions)
    routed, summary = analyze_routing(predictions)

    results_dir = Path("data/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    routed_path = results_dir / f"{args.run_name}_routed_predictions.csv"
    summary_path = results_dir / f"{args.run_name}_routing_summary.json"
    routed.to_csv(routed_path, index=False)
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Saved routed predictions to: {routed_path}")
    print(f"Saved routing summary to: {summary_path}")


if __name__ == "__main__":
    main()
