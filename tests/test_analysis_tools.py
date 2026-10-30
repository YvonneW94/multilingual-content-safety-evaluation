import pandas as pd

from src.agreement import calculate_agreement
from src.analyze_thresholds import evaluate_thresholds
from src.prepare_blind_review import prepare_blind_review
from src.merge_second_review import merge_second_review


def test_thresholds_trade_automation_for_review():
    predictions = pd.DataFrame(
        {
            "predicted_label": ["VIOLENCE", "HATE", "SAFE"],
            "predicted_confidence": [0.96, 0.86, 0.97],
            "adjudicated_label": ["VIOLENCE", "HATE", "SAFE"],
        }
    )

    permissive = evaluate_thresholds(predictions, 0.85, 0.95)
    conservative = evaluate_thresholds(predictions, 0.98, 0.99)

    assert permissive["automated_action_rate"] > conservative[
        "automated_action_rate"
    ]
    assert permissive["human_review_rate"] < conservative["human_review_rate"]


def test_agreement_requires_two_annotators():
    annotations = pd.DataFrame(
        {
            "language": ["en"],
            "annotator_1": ["SAFE"],
            "annotator_2": [""],
        }
    )
    assert calculate_agreement(annotations)["status"] == "insufficient_data"


def test_agreement_calculates_kappa():
    annotations = pd.DataFrame(
        {
            "language": ["en", "en", "zh", "zh"],
            "annotator_1": ["SAFE", "HATE", "SAFE", "HATE"],
            "annotator_2": ["SAFE", "HATE", "SAFE", "SAFE"],
        }
    )
    result = calculate_agreement(annotations)
    assert result["status"] == "complete"
    assert result["overall"]["percent_agreement"] == 0.75


def test_blind_review_hides_existing_labels():
    annotations = pd.DataFrame(
        {
            "content_id": ["A1"],
            "text": ["Example"],
            "language": ["en"],
            "annotator_1": ["SAFE"],
            "adjudicated_label": ["SAFE"],
        }
    )
    review = prepare_blind_review(annotations)
    assert "annotator_1" not in review.columns
    assert "adjudicated_label" not in review.columns
    assert list(review.columns) == [
        "content_id",
        "text",
        "language",
        "annotator_2",
        "annotator_2_rationale",
        "reviewed_at",
    ]


def test_merge_second_review_flags_disagreement():
    annotations = pd.DataFrame(
        {
            "content_id": ["A1", "A2"],
            "annotator_1": ["SAFE", "HATE"],
            "annotator_2": ["", ""],
            "needs_adjudication": [False, False],
        }
    )
    second_review = pd.DataFrame(
        {
            "content_id": ["A1", "A2"],
            "annotator_2": ["SAFE", "HARASSMENT"],
            "annotator_2_rationale": ["", "Borderline target"],
            "reviewed_at": ["2026-10-30", "2026-10-30"],
        }
    )
    merged = merge_second_review(annotations, second_review)
    assert bool(merged.loc[0, "needs_adjudication"]) is False
    assert bool(merged.loc[1, "needs_adjudication"]) is True
