from app.schemas.analysis import BehavioralIndicator


INDICATORS = {
    "problem solving": ["problem", "issue", "challenge", "resolved", "solution", "fix"],
    "collaboration": ["team", "we ", "colleague", "collaborated", "together"],
    "adaptability": ["adapt", "learned", "new", "change", "changed"],
    "accountability": ["responsible", "owned", "my mistake", "accountable"],
    "decision making": ["decided", "decision", "chose", "trade-off"],
    "conflict handling": ["conflict", "disagreement", "resolved", "dispute"],
    "ownership": ["owned", "implemented", "delivered", "responsible"],
    "leadership": ["led", "lead", "mentored", "managed", "guided"],
    "learning attitude": ["learned", "learning", "course", "improved", "studied"],
}


def analyze_behavior(qas) -> list[BehavioralIndicator]:
    results = []
    for name, terms in INDICATORS.items():
        hits = []
        for qa in qas:
            low = qa.answer.lower()
            if any(term in low for term in terms):
                hits.append(qa)

        if not hits:
            results.append(
                BehavioralIndicator(
                    indicator=name,
                    assessment="Limited Evidence",
                    evidence="No meaningful transcript evidence was found for this indicator.",
                    source_question_id=None,
                    confidence=0.08,
                    evidence_status="Limited Evidence",
                    limitation="The supplied transcript does not contain sufficient evidence.",
                )
            )
            continue

        qa = hits[0]
        evidence = qa.answer[:300]
        confidence = min(0.92, 0.55 + 0.08 * len(hits))
        status = "Strong Evidence" if len(hits) >= 2 else "Moderate Evidence"

        results.append(
            BehavioralIndicator(
                indicator=name,
                assessment=f"Evidence suggests {name} is demonstrated in the cited response.",
                evidence=evidence,
                source_question_id=qa.question_id,
                confidence=confidence,
                evidence_status=status,
            )
        )
    return results
