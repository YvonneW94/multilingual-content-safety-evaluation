import pytest

from src.routing import route_prediction


def test_high_confidence_violence_routes_to_action():
    decision = route_prediction("VIOLENCE", 0.94)
    assert decision.action == "AUTOMATED_ACTION"


def test_uncertain_self_harm_routes_to_review():
    decision = route_prediction("SELF_HARM", 0.82)
    assert decision.action == "HUMAN_REVIEW"


def test_high_confidence_safe_content_passes():
    decision = route_prediction("SAFE", 0.91)
    assert decision.action == "PASS"


def test_uncertain_safe_content_is_monitored():
    decision = route_prediction("SAFE", 0.65)
    assert decision.action == "MONITOR"


def test_invalid_confidence_raises_error():
    with pytest.raises(ValueError):
        route_prediction("SAFE", 1.1)
