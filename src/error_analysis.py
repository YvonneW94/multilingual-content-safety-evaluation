import argparse
import json
from pathlib import Path

import pandas as pd


def assign_error_type(row: pd.Series) -> str:
    true_label = row["adjudicated_label"]
    predicted_label = row["predicted_label"]
    if true_label == predicted_label:
        return "CORRECT"
    if true_label == "SAFE" and predicted_label != "SAFE":
        return "FALSE_POSITIVE"
    if true_label != "SAFE" and predicted_label == "SAFE":
        return "FALSE_NEGATIVE"
    return "CROSS_CATEGORY"


def analyze_errors(predictions: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    analyzed = predictions.copy()
    analyzed["error_type"] = analyzed.apply(assign_error_type, axis=1)
    errors = analyzed[analyzed["error_type"] != "CORRECT"].copy()

    summary = {
        "sample_size": len(analyzed),
        "error_count": len(errors),
        "error_rate": len(errors) / len(analyzed) if len(analyzed) else 0.0,
        "error_type_counts": errors["error_type"].value_counts().to_dict(),
        "errors_by_language": errors["language"].value_counts().to_dict(),
        "errors_by_true_label": (
            errors["adjudicated_label"].value_counts().to_dict()
        ),
    }
    if "difficulty" in errors.columns:
        summary["errors_by_difficulty"] = (
            errors["difficulty"].value_counts().to_dict()
        )

    return analyzed, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--run-name", required=True)
    args = parser.parse_args()

    predictions = pd.read_csv(args.predictions)
    analyzed, summary = analyze_errors(predictions)

    results_dir = Path("data/results")
    detailed_path = results_dir / f"{args.run_name}_error_analysis.csv"
    summary_path = results_dir / f"{args.run_name}_error_summary.json"
    analyzed.to_csv(detailed_path, index=False)
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Saved detailed error analysis to: {detailed_path}")
    print(f"Saved error summary to: {summary_path}")


if __name__ == "__main__":
    main()
