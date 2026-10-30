import pandas as pd

from src.analyze_routing import analyze_routing


def test_analyze_routing_reports_review_volume():
    predictions = pd.DataFrame(
        {
            "predicted_label": ["SAFE", "VIOLENCE", "SELF_HARM"],
            "predicted_confidence": [0.95, 0.96, 0.84],
        }
    )

    routed, summary = analyze_routing(predictions)

    assert list(routed["routing_action"]) == [
        "PASS",
        "AUTOMATED_ACTION",
        "HUMAN_REVIEW",
    ]
    assert summary["human_review_rate"] == 1 / 3
    assert summary["automated_action_rate"] == 1 / 3
