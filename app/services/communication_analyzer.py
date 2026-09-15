import re
from collections import Counter
from app.schemas.analysis import CommunicationAnalysis, DimensionScore, FillerAnalysis, STARAnalysis


FILLERS = ["um", "uh", "actually", "basically", "like", "you know", "i mean"]


def _score(value: int, assessment: str, evidence: str, confidence: float, limitation=None):
    return DimensionScore(
        score=max(1, min(10, value)),
        assessment=assessment,
        evidence=evidence,
        confidence=confidence,
        limitation=limitation,
    )


def analyze_communication(qas) -> CommunicationAnalysis:
    if not qas:
        empty = _score(1, "Limited Evidence", "No candidate answers were extracted.", 0.05,
                       "No usable candidate answer was available.")
        return CommunicationAnalysis(
            clarity=empty, relevance=empty, responsiveness=empty, structure=empty,
            conciseness=empty, articulation=empty, professional_communication=empty,
            overall_score=1.0
        )

    scores = {k: [] for k in [
        "clarity", "relevance", "responsiveness", "structure",
        "conciseness", "articulation", "professional_communication"
    ]}

    for qa in qas:
        answer = qa.answer
        words = answer.split()
        n = len(words)
        sentences = max(1, len(re.findall(r"[.!?]", answer)))
        lower = answer.lower()

        direct = 2 if any(k in lower for k in ["i ", "we ", "my ", "our "]) else 1
        structure = 6 + (1 if sentences >= 3 else 0) + (1 if any(x in lower for x in ["first", "then", "finally", "because", "result"]) else 0)
        concise = 8 if n <= 90 else 7 if n <= 160 else 5 if n <= 250 else 3
        relevance = 7 if n >= 12 else 5 if n >= 6 else 3
        clarity = 7 if sentences >= 2 and n >= 15 else 6 if n >= 8 else 4
        articulation = 7 if sentences >= 2 else 6
        professional = 8 if not any(x in lower for x in ["whatever", "don't care", "stupid"] ) else 3
        responsiveness = min(9, relevance + direct)

        evidence = answer[:220]
        vals = {
            "clarity": (clarity, "Understandability based on sentence completeness and explicit explanation."),
            "relevance": (relevance, "Response length and topical alignment signals were used as a transcript-only proxy."),
            "responsiveness": (responsiveness, "Direct first-person or team-action language supports answering the question."),
            "structure": (structure, "Logical connectors and multi-sentence sequencing support organization."),
            "conciseness": (concise, "Answer length was considered as a proxy for unnecessary expansion."),
            "articulation": (articulation, "Ideas are expressed through complete written sentences in the transcript."),
            "professional_communication": (professional, "Interview-appropriate wording was checked from transcript content."),
        }

        for key, (value, assessment) in vals.items():
            scores[key].append(
                _score(value, assessment, evidence, min(0.9, 0.55 + min(n, 120) / 300))
            )

    result = {}
    for key, items in scores.items():
        avg = round(sum(x.score for x in items) / len(items))
        evidence = items[0].evidence if items else "No evidence"
        result[key] = _score(
            avg,
            "Aggregated transcript-based assessment.",
            evidence,
            round(sum(x.confidence for x in items) / len(items), 2),
        )

    overall = round(sum(x.score for x in result.values()) / len(result), 2)
    return CommunicationAnalysis(**result, overall_score=overall)


def analyze_fillers(transcript: str) -> FillerAnalysis:
    lower = transcript.lower()
    counts = {}
    for filler in FILLERS:
        counts[filler] = len(re.findall(r"\b" + re.escape(filler) + r"\b", lower))

    words = re.findall(r"\b[\w']+\b", lower)
    repeated = []
    if len(words) >= 4:
        grams = Counter(" ".join(words[i:i+3]) for i in range(len(words)-2))
        repeated = [g for g, c in grams.most_common(5) if c >= 2]

    return FillerAnalysis(
        counts=counts,
        total_filler_words=sum(counts.values()),
        repeated_phrases=repeated,
    )


def analyze_star(qas) -> list[STARAnalysis]:
    results = []
    behavioral_terms = ["challenge", "conflict", "team", "problem", "difficult", "situation", "lead", "failure"]
    for qa in qas:
        applicable = any(t in qa.question.lower() for t in behavioral_terms)
        if not applicable:
            continue
        text = qa.answer
        low = text.lower()
        components = {
            "situation": any(x in low for x in ["in my previous", "when", "during", "at my company"]),
            "task": any(x in low for x in ["my task", "responsible", "needed to", "was asked"]),
            "action": any(x in low for x in ["i ", "we ", "implemented", "created", "decided", "resolved"]),
            "result": any(x in low for x in ["result", "improved", "reduced", "increased", "achieved", "finally"]),
        }
        missing = [k.title() for k, v in components.items() if not v]
        results.append(
            STARAnalysis(
                question_id=qa.question_id,
                applicable=True,
                situation=text[:160] if components["situation"] else None,
                task=text[:160] if components["task"] else None,
                action=text[:160] if components["action"] else None,
                result=text[:160] if components["result"] else None,
                missing_components=missing,
            )
        )
    return results
