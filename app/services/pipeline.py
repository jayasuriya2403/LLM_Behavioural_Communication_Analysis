from app.schemas.analysis import AnalysisResult
from app.services.transcript_processor import normalize_transcript
from app.services.qa_extractor import extract_question_answers
from app.services.llm_service import llm_service


async def run_pipeline(transcript: str) -> AnalysisResult:
    """
    LLM-only analysis pipeline.

    Deterministic processing is limited to transcript normalization and Q&A
    segmentation. All semantic assessment, evidence interpretation, confidence,
    STAR analysis, filler/repetition interpretation, strengths, improvements and
    scoring are produced by the LLM and validated against the Pydantic schema.
    """
    clean = normalize_transcript(transcript)
    qas = extract_question_answers(clean)

    if not qas:
        raise ValueError(
            "No interviewer-question/candidate-answer pairs could be extracted. "
            "Use speaker labels such as 'Interviewer:' and 'Candidate:'."
        )

    llm_result = await llm_service.analyze(clean)

    # Enforce schema validation. There is deliberately NO fallback analyzer.
    candidate = dict(llm_result)
    candidate["source"] = "interview_transcript"
    candidate["question_answers"] = [q.model_dump() for q in qas]
    candidate.setdefault("generated_by", "llm")
    candidate["generated_by"] = "llm"

    result = AnalysisResult.model_validate(candidate)

    # The question/answer IDs come from our deterministic transcript parser,
    # while all assessment content comes from the LLM.
    result.question_answers = qas
    result.generated_by = "llm"
    return result
