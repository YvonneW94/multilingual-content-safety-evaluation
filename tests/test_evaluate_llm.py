import pandas as pd

from src.evaluate_llm import summarize_results


def test_summarize_results_calculates_product_metrics():
    results = pd.DataFrame(
        {
            "language": ["en", "en", "zh", "zh"],
            "adjudicated_label": [
                "SAFE",
                "VIOLENCE",
                "SAFE",
                "SELF_HARM",
            ],
            "predicted_label": [
                "SAFE",
                "VIOLENCE",
                "HARASSMENT",
                "SELF_HARM",
            ],
            "structured_output_success": [True, True, True, True],
            "latency_seconds": [1.0, 1.2, 0.8, 1.0],
        }
    )

    summary = summarize_results(results)

    assert summary["sample_size"] == 4
    assert summary["high_severity_recall"] == 1.0
    assert summary["safe_false_positive_rate"] == 0.5
    assert summary["structured_output_success_rate"] == 1.0
    assert summary["language_metrics"]["en"]["accuracy"] == 1.0
