import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from src.evaluate_baseline import LABELS, calculate_metrics, use_final_labels
from src.llm_classifier import classify_with_llm, get_model


DATA_PATH = Path("data/processed/pilot_annotations.csv")
RESULTS_DIR = Path("data/results")
PREDICTIONS_PATH = RESULTS_DIR / "llm_predictions.csv"
METRICS_PATH = RESULTS_DIR / "llm_metrics.json"
COMPARISON_PATH = RESULTS_DIR / "model_comparison.json"
RULE_METRICS_PATH = RESULTS_DIR / "rule_baseline_metrics.json"


def summarize_results(results: pd.DataFrame) -> dict:
    y_true = results["adjudicated_label"]
    y_pred = results["predicted_label"]

    language_metrics = {
        language: calculate_metrics(
            group["adjudicated_label"],
            group["predicted_label"],
        )
        for language, group in results.groupby("language")
    }

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y_true, y_pred, labels=LABELS)

    high_severity = results["adjudicated_label"].isin(
        ["SELF_HARM", "VIOLENCE"]
    )
    safe_content = results["adjudicated_label"] == "SAFE"

    high_severity_recall = (
        (
            results.loc[high_severity, "adjudicated_label"]
            == results.loc[high_severity, "predicted_label"]
        ).mean()
        if high_severity.any()
        else 0.0
    )
    safe_false_positive_rate = (
        (results.loc[safe_content, "predicted_label"] != "SAFE").mean()
        if safe_content.any()
        else 0.0
    )

    return {
        "sample_size": len(results),
        "overall_metrics": calculate_metrics(y_true, y_pred),
        "language_metrics": language_metrics,
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "high_severity_recall": high_severity_recall,
        "safe_false_positive_rate": safe_false_positive_rate,
        "structured_output_success_rate": results[
            "structured_output_success"
        ].mean(),
        "mean_latency_seconds": results["latency_seconds"].mean(),
    }


def load_cached_predictions(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    cached = pd.read_csv(path).fillna("")
    return {
        row["content_id"]: row.to_dict()
        for _, row in cached.iterrows()
        if row.get("structured_output_success") in (True, "True", "true", 1)
    }


def save_predictions(records: list[dict], path: Path) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(path, index=False)


def build_comparison(llm_metrics: dict, rule_metrics_path: Path) -> dict:
    comparison = {"llm": llm_metrics}
    if rule_metrics_path.exists():
        with rule_metrics_path.open(encoding="utf-8") as file:
            rule_metrics = json.load(file)
        comparison["rule_based"] = {
            "sample_size": rule_metrics["sample_size"],
            "overall_metrics": rule_metrics["overall_metrics"],
            "language_metrics": rule_metrics["language_metrics"],
            "classification_report": rule_metrics["classification_report"],
            "confusion_matrix": rule_metrics["confusion_matrix"],
        }
        comparison["macro_f1_lift"] = (
            llm_metrics["overall_metrics"]["macro_f1"]
            - rule_metrics["overall_metrics"]["macro_f1"]
        )
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--run-name", default="llm")
    parser.add_argument("--rule-run-name", default="rule_baseline")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore cached successful predictions.",
    )
    args = parser.parse_args()

    data_path = args.data
    predictions_path = RESULTS_DIR / f"{args.run_name}_predictions.csv"
    metrics_path = RESULTS_DIR / f"{args.run_name}_metrics.json"
    comparison_path = RESULTS_DIR / f"{args.run_name}_comparison.json"
    rule_metrics_path = RESULTS_DIR / f"{args.rule_run_name}_metrics.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    dataset = use_final_labels(pd.read_csv(data_path))
    if args.limit:
        dataset = dataset.head(args.limit)

    cached = (
        {} if args.refresh else load_cached_predictions(predictions_path)
    )
    records = []

    for index, row in dataset.iterrows():
        content_id = row["content_id"]
        if content_id in cached:
            records.append(cached[content_id])
            print(f"[{index + 1}/{len(dataset)}] cached {content_id}")
            continue

        started = time.perf_counter()
        try:
            result = classify_with_llm(row["text"], row["language"])
            record = {
                **row.to_dict(),
                "model": get_model(),
                "predicted_label": result.label,
                "predicted_confidence": result.confidence,
                "policy_reason": result.policy_reason,
                "evidence_span": result.evidence_span,
                "structured_output_success": True,
                "latency_seconds": round(time.perf_counter() - started, 3),
                "error": "",
            }
            print(
                f"[{index + 1}/{len(dataset)}] {content_id}: "
                f"{result.label} ({result.confidence:.2f})"
            )
        except Exception as error:
            record = {
                **row.to_dict(),
                "model": get_model(),
                "predicted_label": "",
                "predicted_confidence": "",
                "policy_reason": "",
                "evidence_span": "",
                "structured_output_success": False,
                "latency_seconds": round(time.perf_counter() - started, 3),
                "error": str(error),
            }
            print(f"[{index + 1}/{len(dataset)}] {content_id}: ERROR {error}")

        records.append(record)
        save_predictions(records, predictions_path)

    results = pd.DataFrame(records)
    successful = results[results["structured_output_success"] == True].copy()
    if len(successful) != len(dataset):
        failed = len(dataset) - len(successful)
        raise RuntimeError(
            f"{failed} classifications failed. Inspect {predictions_path} "
            "and rerun to resume."
        )

    metrics = summarize_results(successful)
    metrics.update(
        {
            "dataset": str(data_path),
            "model": get_model(),
            "labels": LABELS,
        }
    )
    with metrics_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    comparison = build_comparison(metrics, rule_metrics_path)
    with comparison_path.open("w", encoding="utf-8") as file:
        json.dump(comparison, file, ensure_ascii=False, indent=2)

    print("\nLLM evaluation complete")
    print(f"Sample size: {metrics['sample_size']}")
    print(f"Macro F1: {metrics['overall_metrics']['macro_f1']:.3f}")
    print(f"High-severity recall: {metrics['high_severity_recall']:.3f}")
    print(
        "Safe-content false-positive rate: "
        f"{metrics['safe_false_positive_rate']:.3f}"
    )
    print(f"Saved predictions to: {predictions_path}")
    print(f"Saved comparison to: {comparison_path}")


if __name__ == "__main__":
    main()
