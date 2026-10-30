from dataclasses import dataclass


HIGH_SEVERITY_LABELS = {"SELF_HARM", "VIOLENCE"}


@dataclass(frozen=True)
class RoutingDecision:
    action: str
    reason: str


def route_prediction(label: str, confidence: float) -> RoutingDecision:
    """Route a model prediction to action, review, or monitoring.

    Confidence values are heuristic routing inputs rather than calibrated
    probabilities. Conservative thresholds keep uncertain or severe cases in
    the human-review loop.
    """

    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    if label in HIGH_SEVERITY_LABELS:
        if confidence >= 0.90:
            return RoutingDecision(
                action="AUTOMATED_ACTION",
                reason="High-confidence, high-severity prediction",
            )
        return RoutingDecision(
            action="HUMAN_REVIEW",
            reason="High-severity prediction requires review below 0.90",
        )

    if label in {"HATE", "HARASSMENT"}:
        if confidence >= 0.85:
            return RoutingDecision(
                action="AUTOMATED_ACTION",
                reason="High-confidence policy violation",
            )
        return RoutingDecision(
            action="HUMAN_REVIEW",
            reason="Moderate-confidence policy violation",
        )

    if label == "SAFE":
        if confidence >= 0.80:
            return RoutingDecision(
                action="PASS",
                reason="High-confidence safe prediction",
            )
        return RoutingDecision(
            action="MONITOR",
            reason="Low-confidence safe prediction",
        )

    raise ValueError(f"unsupported label: {label}")
