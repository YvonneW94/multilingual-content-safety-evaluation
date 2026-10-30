import pandas as pd
import pytest

from src.calibration import calculate_calibration


def test_perfect_calibration_has_zero_error():
    predictions = pd.DataFrame(
        {
            "adjudicated_label": ["SAFE", "HATE"],
            "predicted_label": ["SAFE", "SAFE"],
            "predicted_confidence": [1.0, 0.0],
        }
    )
    _, summary = calculate_calibration(predictions, bin_count=2)
    assert summary["expected_calibration_error"] == 0.0
    assert summary["brier_score"] == 0.0


def test_overconfident_errors_increase_brier_score():
    predictions = pd.DataFrame(
        {
            "adjudicated_label": ["HATE", "VIOLENCE"],
            "predicted_label": ["SAFE", "SAFE"],
            "predicted_confidence": [0.9, 0.8],
        }
    )
    _, summary = calculate_calibration(predictions, bin_count=2)
    assert summary["brier_score"] == pytest.approx(0.725)


def test_invalid_confidence_is_rejected():
    predictions = pd.DataFrame(
        {
            "adjudicated_label": ["SAFE"],
            "predicted_label": ["SAFE"],
            "predicted_confidence": [1.2],
        }
    )
    with pytest.raises(ValueError):
        calculate_calibration(predictions)
