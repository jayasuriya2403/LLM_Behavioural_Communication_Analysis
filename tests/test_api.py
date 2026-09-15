from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint():
    response = client.post(
        "/api/v1/analyze",
        json={
            "transcript": (
                "Interviewer: Tell me about a challenge.\n"
                "Candidate: I solved a difficult problem with my team and improved the result."
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] is not None
    assert data["question_answers"][0]["question_id"] == "Q01"
