import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.analysis import AnalysisRecord
from app.schemas.analysis import AnalysisResult, TranscriptRequest
from app.services.pipeline import run_pipeline
from app.services.llm_service import LLMUnavailableError
from app.services.report_generator import candidate_report, recruiter_report
from app.core.config import settings


router = APIRouter(prefix="/api/v1", tags=["Interview Analysis"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(payload: TranscriptRequest, db: Session = Depends(get_db)):
    if len(payload.transcript) > settings.max_transcript_chars:
        raise HTTPException(status_code=413, detail="Transcript is too large.")

    try:
        result = await run_pipeline(payload.transcript)
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record = AnalysisRecord(
        transcript=payload.transcript,
        result_json=result.model_dump_json(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    result.analysis_id = record.id
    record.result_json = result.model_dump_json()
    db.commit()
    return result


@router.post("/analyze/upload", response_model=AnalysisResult)
async def analyze_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt transcript files are supported.")
    raw = await file.read()
    transcript = raw.decode("utf-8", errors="replace")
    return await analyze(TranscriptRequest(transcript=transcript), db)


def _get_record(analysis_id: int, db: Session):
    record = db.get(AnalysisRecord, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return record


@router.get("/analyses/{analysis_id}", response_model=AnalysisResult)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    record = _get_record(analysis_id, db)
    return AnalysisResult.model_validate_json(record.result_json)


@router.get("/analyses/{analysis_id}/json")
def get_json(analysis_id: int, db: Session = Depends(get_db)):
    record = _get_record(analysis_id, db)
    return json.loads(record.result_json)


@router.get("/analyses/{analysis_id}/candidate-report", response_class=HTMLResponse)
def get_candidate_report(analysis_id: int, db: Session = Depends(get_db)):
    record = _get_record(analysis_id, db)
    result = AnalysisResult.model_validate_json(record.result_json)
    return candidate_report(result)


@router.get("/analyses/{analysis_id}/recruiter-report", response_class=HTMLResponse)
def get_recruiter_report(analysis_id: int, db: Session = Depends(get_db)):
    record = _get_record(analysis_id, db)
    result = AnalysisResult.model_validate_json(record.result_json)
    return recruiter_report(result)
