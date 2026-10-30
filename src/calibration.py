import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def calculate_calibration(
    predictions: pd.DataFrame,
    bin_count: int = 10,
) -> tuple[pd.DataFrame, dict]:
    evaluated = predictions.copy()
    evaluated["correct"] = (
        evaluated["adjudicated_label"] == evaluated["predicted_label"]
    ).astype(int)
    confidence = evaluated["predicted_confidence"].astype(float)
    if ((confidence < 0) | (confidence > 1)).any():
        raise ValueError("All confidence values must be between 0 and 1.")

    edges = np.linspace(0, 1, bin_count + 1)
    evaluated["confidence_bin"] = pd.cut(
        confidence,
        bins=edges,
        include_lowest=True,
        duplicates="drop",
    )
    bins = (
        evaluated.groupby("confidence_bin", observed=True)
        .agg(
            sample_size=("correct", "size"),
            mean_confidence=("predicted_confidence", "mean"),
            empirical_accuracy=("correct", "mean"),
        )
        .reset_index()
    )
    bins["confidence_bin"] = bins["confidence_bin"].astype(str)
    bins["absolute_gap"] = (
        bins["mean_confidence"] - bins["empirical_accuracy"]
    ).abs()
    bins["weighted_gap"] = (
        bins["sample_size"] / len(evaluated) * bins["absolute_gap"]
    )

    summary = {
        "sample_size": len(evaluated),
        "mean_confidence": confidence.mean(),
        "empirical_accuracy": evaluated["correct"].mean(),
        "expected_calibration_error": bins["weighted_gap"].sum(),
        "brier_score": ((confidence - evaluated["correct"]) ** 2).mean(),
        "bin_count": bin_count,
    }
    return bins, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--bins", type=int, default=10)
    args = parser.parse_args()

    predictions = pd.read_csv(args.predictions)
    bins, summary = calculate_calibration(predictions, args.bins)

    results_dir = Path("data/results")
    bins_path = results_dir / f"{args.run_name}_calibration_bins.csv"
    summary_path = results_dir / f"{args.run_name}_calibration_summary.json"
    bins.to_csv(bins_path, index=False)
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Saved calibration bins to: {bins_path}")
    print(f"Saved calibration summary to: {summary_path}")


if __name__ == "__main__":
    main()
