# LLM_Behavioural_Communication_Analysis

This implementation follows the supplied task workflow:

> Transcript Input → Clean & Segment → Extract Q&A → Analyze Communication → Analyze Behaviour → Extract Evidence → Determine Confidence → Calculate Scores → Generate Strengths & Improvements → Candidate Report → Recruiter Report

## Features

- Transcript upload or paste
- Speaker detection and transcript normalization
- Stable Question IDs and Answer IDs
- Question–answer extraction
- Communication analysis:
  - clarity
  - relevance
  - responsiveness
  - structure
  - conciseness
  - articulation
  - professional communication
- Behavioural analysis:
  - problem solving
  - collaboration
  - adaptability
  - accountability
  - decision making
  - conflict handling
  - ownership
  - leadership
  - learning attitude
- Filler-word and repetition analysis
- Optional STAR analysis for behavioural questions
- Evidence for important assessments
- Confidence/evidence strength and limitations
- Documented 1–10 scoring rubric
- LLM structured JSON output using Ollama
- LLM-only analysis: Ollama/Llama 3.2 is required
- SQLite persistence
- Candidate-facing and recruiter-facing reports
- REST API + lightweight web UI
- Sample transcripts
- Automated tests
- Architecture diagram
- Prompt versioning
- Demo script

## Requirements

- Python 3.11+
- Optional: Ollama for local LLM analysis

Recommended Ollama models:

```text
llama3.2
nomic-embed-text
```

`nomic-embed-text` is not required by this MVP because the supplied workflow does not require a vector database. It can be introduced later for evidence retrieval across large interview corpora.

## Installation

### Windows PowerShell

```powershell
cd vellei_interview_assessment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Optional: Ollama

Install Ollama, then pull the configured chat model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running.

Default configuration:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2
LLM_ENABLED=true
```

Ollama/Llama 3.2 is mandatory. If Ollama is unavailable or returns invalid structured JSON, the API returns a clear error and does not perform non-LLM analysis.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- Web UI: `http://127.0.0.1:8000`
- Swagger API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## API

### Analyze pasted transcript

```http
POST /api/v1/analyze
Content-Type: application/json
```

Example:

```json
{
  "transcript": "Interviewer: Tell me about a challenging project.\nCandidate: In my previous company, I worked on an e-commerce project..."
}
```

### Analyze uploaded transcript

```http
POST /api/v1/analyze/upload
```

Accepts `.txt` files.

### Retrieve analysis

```http
GET /api/v1/analyses/{analysis_id}
```

### Candidate report

```http
GET /api/v1/analyses/{analysis_id}/candidate-report
```

### Recruiter report

```http
GET /api/v1/analyses/{analysis_id}/recruiter-report
```

### Raw structured JSON

```http
GET /api/v1/analyses/{analysis_id}/json
```

## Example curl

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d @data/samples/strong_candidate.json
```

## Scoring methodology

Every communication dimension is scored 1–10.

- 1–3: Low
- 4–6: Medium
- 7–8: Good
- 9–10: Strong

Scores are generated from evidence-backed component assessments. The overall communication score is the arithmetic mean of the seven communication dimensions.

Behavioural indicators are not forced into a numeric score when the transcript lacks evidence. They carry an evidence status:

- Strong Evidence
- Moderate Evidence
- Weak Evidence
- Limited Evidence

See `docs/scoring_methodology.md`.

## Testing

```bash
pytest -q
```

The test suite covers:

- transcript parsing
- Q&A IDs
- filler detection
- STAR detection
- evidence grounding
- limited evidence behaviour
- scoring consistency
- API flow
- report generation

