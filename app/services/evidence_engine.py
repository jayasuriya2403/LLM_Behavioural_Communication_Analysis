from app.schemas.analysis import BehavioralIndicator


def validate_behavioral_evidence(indicators: list[BehavioralIndicator]) -> list[BehavioralIndicator]:
    """Prevent a positive behavioural assessment from surviving without evidence."""
    for item in indicators:
        if not item.evidence or item.evidence_status == "Limited Evidence":
            item.assessment = "Limited Evidence"
            item.confidence = min(item.confidence, 0.1)
            item.evidence_status = "Limited Evidence"
            item.limitation = item.limitation or "Insufficient interview evidence."
    return indicators
