import argparse
from pathlib import Path

import pandas as pd


HARMFUL_LABELS = {"HATE", "HARASSMENT", "VIOLENCE", "SELF_HARM"}


def evaluate_thresholds(
    predictions: pd.DataFrame,
    harmful_threshold: float,
    safe_threshold: float,
) -> dict:
    actions = []
    for _, row in predictions.iterrows():
        label = row["predicted_label"]
        confidence = float(row["predicted_confidence"])
        if label in HARMFUL_LABELS:
            action = (
                "AUTOMATED_ACTION"
                if confidence >= harmful_threshold
                else "HUMAN_REVIEW"
            )
        else:
            action = "PASS" if confidence >= safe_threshold else "MONITOR"
        actions.append(action)

    evaluated = predictions.copy()
    evaluated["routing_action"] = actions
    automated = evaluated["routing_action"] == "AUTOMATED_ACTION"
    passed = evaluated["routing_action"] == "PASS"

    automated_errors = (
        evaluated.loc[automated, "predicted_label"]
        != evaluated.loc[automated, "adjudicated_label"]
    )
    unsafe_passes = evaluated.loc[passed, "adjudicated_label"].isin(
        HARMFUL_LABELS
    )

    return {
        "harmful_threshold": harmful_threshold,
        "safe_threshold": safe_threshold,
        "automated_action_rate": automated.mean(),
        "human_review_rate": (
            evaluated["routing_action"] == "HUMAN_REVIEW"
        ).mean(),
        "pass_rate": passed.mean(),
        "monitor_rate": (
            evaluated["routing_action"] == "MONITOR"
        ).mean(),
        "automated_action_error_rate": (
            automated_errors.mean() if automated.any() else 0.0
        ),
        "unsafe_pass_rate": unsafe_passes.mean() if passed.any() else 0.0,
    }


def run_sensitivity_analysis(predictions: pd.DataFrame) -> pd.DataFrame:
    thresholds = [0.80, 0.85, 0.90, 0.95, 0.98, 0.99]
    records = [
        evaluate_thresholds(predictions, harmful, safe)
        for harmful in thresholds
        for safe in thresholds
    ]
    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    args = parser.parse_args()

    predictions = pd.read_csv(args.predictions)
    analysis = run_sensitivity_analysis(predictions)
    output = Path("data/results") / f"{args.run_name}_threshold_sensitivity.csv"
    analysis.to_csv(output, index=False)

    print(analysis.to_string(index=False))
    print(f"\nSaved threshold sensitivity analysis to: {output}")


if __name__ == "__main__":
    main()
