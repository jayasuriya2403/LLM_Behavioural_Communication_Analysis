from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


EvidenceStatus = Literal[
    "Strong Evidence",
    "Moderate Evidence",
    "Weak Evidence",
    "Limited Evidence",
]


class TranscriptRequest(BaseModel):
    transcript: str = Field(min_length=10)


class QAItem(BaseModel):
    question_id: str
    question: str
    answer_id: str
    answer: str


class DimensionScore(BaseModel):
    score: int = Field(ge=1, le=10)
    assessment: str
    evidence: str
    confidence: float = Field(ge=0, le=1)
    limitation: Optional[str] = None


class CommunicationAnalysis(BaseModel):
    clarity: DimensionScore
    relevance: DimensionScore
    responsiveness: DimensionScore
    structure: DimensionScore
    conciseness: DimensionScore
    articulation: DimensionScore
    professional_communication: DimensionScore
    overall_score: float = Field(ge=1, le=10)


class BehavioralIndicator(BaseModel):
    indicator: str
    assessment: str
    evidence: str
    source_question_id: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    evidence_status: EvidenceStatus
    limitation: Optional[str] = None

    @field_validator("evidence_status", mode="before")
    @classmethod
    def normalize_evidence_status(cls, value):
        """
        Normalize common LLM variations into the controlled rubric.

        This does not generate an assessment or fallback analysis.
        It only normalizes the label returned by the LLM.
        """
        if value is None:
            return "Limited Evidence"

        value = str(value).strip()

        aliases = {
            "Good": "Strong Evidence",
            "Strong": "Strong Evidence",
            "Moderate": "Moderate Evidence",
            "Weak": "Weak Evidence",
            "Limited": "Limited Evidence",
            "Insufficient Evidence": "Limited Evidence",
            "No Evidence": "Limited Evidence",
        }

        return aliases.get(value, value)


class FillerAnalysis(BaseModel):
    counts: dict[str, int] = Field(default_factory=dict)
    total_filler_words: int = Field(ge=0)
    repeated_phrases: List[str] = Field(default_factory=list)


class STARAnalysis(BaseModel):
    question_id: str
    applicable: bool
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    missing_components: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    analysis_id: Optional[int] = None
    source: str = "interview_transcript"

    question_answers: List[QAItem] = Field(default_factory=list)

    communication: CommunicationAnalysis

    behavioral_indicators: List[BehavioralIndicator] = Field(
        default_factory=list
    )

    filler_analysis: FillerAnalysis

    star_analysis: List[STARAnalysis] = Field(
        default_factory=list
    )

    strengths: List[str] = Field(default_factory=list)

    improvement_areas: List[str] = Field(
        default_factory=list
    )

    limitations: List[str] = Field(default_factory=list)

    overall_score: float = Field(ge=1, le=10)

    recommendation_support: str

    generated_by: str = "llm"