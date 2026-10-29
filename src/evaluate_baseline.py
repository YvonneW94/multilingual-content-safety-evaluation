import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.rule_based_classifier import classify_as_dict


DATA_PATH = Path("data/processed/pilot_annotations.csv")
RESULTS_DIR = Path("data/results")
PREDICTIONS_PATH = RESULTS_DIR / "rule_baseline_predictions.csv"
METRICS_PATH = RESULTS_DIR / "rule_baseline_metrics.json"

LABELS = [
    "SAFE",
    "HATE",
    "HARASSMENT",
    "VIOLENCE",
    "SELF_HARM",
]


def calculate_metrics(
    y_true: pd.Series,
    y_pred: pd.Series,
) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": precision_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="macro",
            zero_division=0,
        ),
        "macro_recall": recall_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="macro",
            zero_division=0,
        ),
        "macro_f1": f1_score(
            y_true,
            y_pred,
            labels=LABELS,
            average="macro",
            zero_division=0,
        ),
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    predictions = df.apply(
        lambda row: classify_as_dict(
            row["text"],
            row["language"],
        ),
        axis=1,
    )

    prediction_df = pd.DataFrame(predictions.tolist())

    results = pd.concat(
        [
            df.reset_index(drop=True),
            prediction_df.add_prefix("predicted_"),
        ],
        axis=1,
    )

    y_true = results["adjudicated_label"]
    y_pred = results["predicted_label"]

    overall_metrics = calculate_metrics(y_true, y_pred)

    language_metrics = {}
    for language, group in results.groupby("language"):
        language_metrics[language] = calculate_metrics(
            group["adjudicated_label"],
            group["predicted_label"],
        )

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
        output_dict=True,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    output = {
        "dataset": str(DATA_PATH),
        "sample_size": len(results),
        "labels": LABELS,
        "overall_metrics": overall_metrics,
        "language_metrics": language_metrics,
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }

    results.to_csv(PREDICTIONS_PATH, index=False)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("\nOverall metrics")
    print("----------------")
    for metric, value in overall_metrics.items():
        print(f"{metric}: {value:.3f}")

    print("\nMetrics by language")
    print("-------------------")
    for language, metrics in language_metrics.items():
        print(f"\n{language}")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.3f}")

    print("\nClassification report")
    print("---------------------")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=LABELS,
            zero_division=0,
        )
    )

    print("\nConfusion matrix")
    print("----------------")
    print(pd.DataFrame(matrix, index=LABELS, columns=LABELS))

    errors = results[
        results["adjudicated_label"] != results["predicted_label"]
    ]

    print(f"\nIncorrect predictions: {len(errors)}")

    if not errors.empty:
        print(
            errors[
                [
                    "content_id",
                    "language",
                    "adjudicated_label",
                    "predicted_label",
                    "text",
                ]
            ].to_string(index=False)
        )

    print(f"\nSaved predictions to: {PREDICTIONS_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
