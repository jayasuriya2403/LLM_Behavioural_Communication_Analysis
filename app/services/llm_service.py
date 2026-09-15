import json
from pathlib import Path

import httpx

from app.core.config import settings


class LLMUnavailableError(RuntimeError):
    """Raised when the required local LLM cannot be reached or returns invalid output."""


class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url.strip().rstrip("/")
        self.model = settings.ollama_chat_model.strip()

        # Project root:
        # app/services/llm_service.py
        #       -> services
        #       -> app
        #       -> project root
        self.project_root = Path(__file__).resolve().parents[2]

        self.system_prompt_path = (
            self.project_root / "app" / "prompts" / "v1_system.txt"
        )

        self.schema_path = (
            self.project_root / "app" / "prompts" / "v1_analysis_schema.json"
        )

    async def analyze(self, transcript: str) -> dict:
        # This project is intentionally LLM-only.
        if not settings.llm_enabled:
            raise LLMUnavailableError(
                "LLM is disabled. This project requires the LLM. "
                "Set LLM_ENABLED=true in .env."
            )

        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        prompt = self._build_prompt(transcript)

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": self._system_prompt(),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "options": {
                "temperature": 0.1,
            },
        }

        url = f"{self.base_url}/api/chat"

        try:
            timeout = httpx.Timeout(
                connect=10.0,
                read=600.0,
                write=60.0,
                pool=30.0,
            )

            async with httpx.AsyncClient(timeout=timeout) as client:

                # First verify Ollama is reachable.
                try:
                    health_response = await client.get(
                        f"{self.base_url}/api/tags"
                    )
                    health_response.raise_for_status()
                except httpx.HTTPError as exc:
                    raise LLMUnavailableError(
                        f"Cannot reach Ollama at {self.base_url}. "
                        f"Original error: {exc}"
                    ) from exc

                # Verify the requested model exists.
                try:
                    models_data = health_response.json()
                except ValueError as exc:
                    raise LLMUnavailableError(
                        "Ollama returned invalid JSON from /api/tags."
                    ) from exc

                models = models_data.get("models", [])

                model_names = {
                    model.get("name")
                    for model in models
                    if isinstance(model, dict)
                }

                if (
                    self.model not in model_names
                    and f"{self.model}:latest" not in model_names
                ):
                    raise LLMUnavailableError(
                        f"Model '{self.model}' is not available in Ollama. "
                        f"Installed models: {sorted(model_names)}"
                    )

                # Call Llama 3.2.
                try:
                    response = await client.post(
                        url,
                        json=payload,
                    )
                except httpx.ConnectError as exc:
                    raise LLMUnavailableError(
                        f"Connection to Ollama failed at {url}: {exc}"
                    ) from exc
                except httpx.TimeoutException as exc:
                    raise LLMUnavailableError(
                        f"Ollama request timed out after 180 seconds."
                    ) from exc
                except httpx.RequestError as exc:
                    raise LLMUnavailableError(
                        f"Ollama request failed: {exc}"
                    ) from exc

                # Do NOT hide the actual HTTP error.
                if response.status_code >= 400:
                    raise LLMUnavailableError(
                        f"Ollama returned HTTP {response.status_code}: "
                        f"{response.text[:1000]}"
                    )

                try:
                    body = response.json()
                except ValueError as exc:
                    raise LLMUnavailableError(
                        "Ollama returned a non-JSON HTTP response."
                    ) from exc

                message = body.get("message", {})

                if not isinstance(message, dict):
                    raise LLMUnavailableError(
                        "Ollama response does not contain a valid message object."
                    )

                content = message.get("content")

                if not content or not isinstance(content, str):
                    raise LLMUnavailableError(
                        "Ollama returned an empty LLM response."
                    )

                # Llama is required to return JSON.
                try:
                    result = json.loads(content)
                except json.JSONDecodeError as exc:
                    raise LLMUnavailableError(
                        "Llama 3.2 returned invalid JSON. "
                        f"Raw response: {content[:1000]}"
                    ) from exc

                if not isinstance(result, dict):
                    raise LLMUnavailableError(
                        "Llama 3.2 returned JSON, but the root value is not an object."
                    )

                return result

        except LLMUnavailableError:
            raise

        except Exception as exc:
            raise LLMUnavailableError(
                f"Unexpected LLM analysis error: {type(exc).__name__}: {exc}"
            ) from exc

    def _system_prompt(self) -> str:
        if not self.system_prompt_path.exists():
            raise LLMUnavailableError(
                f"System prompt file not found: {self.system_prompt_path}"
            )

        return self.system_prompt_path.read_text(
            encoding="utf-8"
        )

    def _build_prompt(self, transcript: str) -> str:
        if not self.schema_path.exists():
            raise LLMUnavailableError(
                f"Analysis schema file not found: {self.schema_path}"
            )

        schema = self.schema_path.read_text(
            encoding="utf-8"
        )

        return f"""
Analyze ONLY the supplied interview transcript.

You MUST perform the semantic communication and behavioural analysis using
your LLM reasoning. Do not use external knowledge.

Required workflow:

1. Analyze the candidate answers.
2. Assess communication across all seven dimensions:
   - clarity
   - relevance
   - responsiveness
   - structure
   - conciseness
   - articulation
   - professional communication

3. Assess the defined behavioural indicators:
   - problem solving
   - collaboration
   - adaptability
   - accountability
   - decision making
   - conflict handling
   - ownership
   - leadership indicators
   - learning attitude

4. Extract supporting evidence.
5. Assign confidence based on evidence strength.
6. Return "Limited Evidence" when the transcript does not support an assessment.
7. Analyze filler words and repetition only when supported by the transcript.
8. Analyze STAR components for applicable behavioural questions.
9. Generate strengths and improvement areas.
10. Calculate the communication overall score according to the supplied rubric.
11. Include limitations.
12. Return ONLY valid JSON matching the supplied schema.

GROUNDING RULES:

- Analyze only the supplied transcript.
- Never invent evidence.
- Evidence must be a concise quote or faithful summary of the transcript.
- Include source_question_id wherever behavioural evidence is available.
- Do not diagnose personality, psychology, medical conditions, or mental health.
- Do not assess facial expression, body language, or voice characteristics from text.
- Do not make a final hiring decision.
- If evidence is insufficient, explicitly return "Limited Evidence".
- Do not use external knowledge.
- Do not return markdown.
- Return valid JSON only.

SCHEMA:

{schema}

TRANSCRIPT:

{transcript}
"""


llm_service = LLMService()