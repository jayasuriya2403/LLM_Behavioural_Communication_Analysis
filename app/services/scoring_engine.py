from statistics import mean


def communication_overall(communication) -> float:
    values = [
        communication.clarity.score,
        communication.relevance.score,
        communication.responsiveness.score,
        communication.structure.score,
        communication.conciseness.score,
        communication.articulation.score,
        communication.professional_communication.score,
    ]
    return round(mean(values), 2)


def score_band(score: float) -> str:
    if score <= 3:
        return "Low"
    if score <= 6:
        return "Medium"
    if score <= 8:
        return "Good"
    return "Strong"


def generate_strengths_improvements(communication, behavioral, filler, star):
    dimensions = {
        "clarity": communication.clarity.score,
        "relevance": communication.relevance.score,
        "responsiveness": communication.responsiveness.score,
        "structure": communication.structure.score,
        "conciseness": communication.conciseness.score,
        "articulation": communication.articulation.score,
        "professional communication": communication.professional_communication.score,
    }
    strengths = [f"Strong {k} ({v}/10)." for k, v in dimensions.items() if v >= 8][:4]
    improvements = [f"Improve {k} ({v}/10)." for k, v in dimensions.items() if v <= 6][:4]

    if filler.total_filler_words:
        improvements.append(f"Reduce filler-word usage ({filler.total_filler_words} detected).")
    missing_star = sorted({m for s in star for m in s.missing_components})
    if missing_star:
        improvements.append("Strengthen behavioural answers by adding missing STAR components: " + ", ".join(missing_star[:4]) + ".")

    if not strengths:
        strengths.append("The transcript provides some usable evidence, but no dimension reached the strong threshold.")
    if not improvements:
        improvements.append("Continue maintaining the current communication structure and directness.")

    return strengths, improvements
