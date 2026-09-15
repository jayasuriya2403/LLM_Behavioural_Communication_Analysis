import pytest
from app.services.pipeline import run_pipeline
from app.services.qa_extractor import extract_question_answers
from app.services.communication_analyzer import analyze_fillers
from app.services.scoring_engine import score_band


def test_qa_ids():
    text = "Interviewer: Tell me about yourself.\nCandidate: I am a developer."
    qas = extract_question_answers(text)
    assert len(qas) == 1
    assert qas[0].question_id == "Q01"
    assert qas[0].answer_id == "A01"


def test_filler_detection():
    result = analyze_fillers("Candidate: Um, I basically like this, you know, approach.")
    assert result.total_filler_words >= 3


def test_score_bands():
    assert score_band(2) == "Low"
    assert score_band(5) == "Medium"
    assert score_band(7) == "Good"
    assert score_band(9) == "Strong"


@pytest.mark.asyncio
async def test_limited_evidence():
    transcript = (
        "Interviewer: Tell me about leadership.\n"
        "Candidate: I completed my assigned tasks.\n"
    )
    result = await run_pipeline(transcript)
    leadership = next(x for x in result.behavioral_indicators if x.indicator == "leadership")
    assert leadership.evidence_status == "Limited Evidence"
    assert leadership.confidence <= 0.1


@pytest.mark.asyncio
async def test_pipeline_generates_qas():
    transcript = (
        "Interviewer: Tell me about a problem.\n"
        "Candidate: I found a problem and fixed it with my team.\n"
    )
    result = await run_pipeline(transcript)
    assert result.question_answers[0].question_id == "Q01"
    assert result.overall_score >= 1
    assert result.overall_score <= 10
