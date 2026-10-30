import pandas as pd

from src.error_analysis import analyze_errors, assign_error_type


def test_assign_error_types():
    assert assign_error_type(
        pd.Series({"adjudicated_label": "SAFE", "predicted_label": "HATE"})
    ) == "FALSE_POSITIVE"
    assert assign_error_type(
        pd.Series({"adjudicated_label": "HATE", "predicted_label": "SAFE"})
    ) == "FALSE_NEGATIVE"
    assert assign_error_type(
        pd.Series(
            {"adjudicated_label": "HATE", "predicted_label": "HARASSMENT"}
        )
    ) == "CROSS_CATEGORY"


def test_analyze_errors_slices_failures():
    predictions = pd.DataFrame(
        {
            "language": ["en", "zh", "zh"],
            "difficulty": ["easy", "hard", "hard"],
            "adjudicated_label": ["SAFE", "HATE", "VIOLENCE"],
            "predicted_label": ["SAFE", "SAFE", "HARASSMENT"],
        }
    )
    analyzed, summary = analyze_errors(predictions)
    assert len(analyzed) == 3
    assert summary["error_count"] == 2
    assert summary["error_type_counts"] == {
        "FALSE_NEGATIVE": 1,
        "CROSS_CATEGORY": 1,
    }
    assert summary["errors_by_language"] == {"zh": 2}
