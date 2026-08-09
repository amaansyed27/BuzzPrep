from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.db.database import Database
from app.interview.engine import AdaptiveInterviewEngine
from app.llm.fake import FakeLLMProvider
from app.main import create_app
from app.memory.fake import InMemoryMemoryService
from app.profiling.loader import load_candidates
from app.services.session import InterviewSessionRepository


def candidate(candidate_id: str) -> dict:
    record = next(item for item in load_candidates() if item.member.candidate_id == candidate_id)
    return record.model_dump(mode="json", by_alias=True)


def test_complete_fake_interview_persists_workspace_memory_and_hard_gate(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'full-e2e.db'}"
    memory = InMemoryMemoryService()
    provider = FakeLLMProvider()
    app = create_app(
        database_url=database_url,
        interview_engine=AdaptiveInterviewEngine(provider, memory),
        memory_service=memory,
    )

    workspace = {
        "nodes": [],
        "edges": [],
        "config": {"timeout_ms": 1200},
        "editors": {},
        "submissions": [],
        "events": [
            {
                "id": "evt-e2e-configure",
                "type": "configure",
                "timestamp": "2026-08-09T00:00:00Z",
                "payload": {"configKey": "timeout_ms", "value": 1200},
            }
        ],
        "workspaceActive": True,
        "challengeId": "e2e-challenge",
    }

    with TestClient(app) as client:
        started = client.post(
            "/api/interview",
            json={"sessionId": "e2e-primary", "candidate": candidate("CAND-001")},
        )
        assert started.status_code == 200
        assert started.json()["done"] is False
        assert started.json()["progress"]["questionsAsked"] == 1

        for answer_number in range(1, 8):
            payload = {
                "sessionId": "e2e-primary",
                "message": (
                    f"Answer {answer_number}: I choose this because it balances latency and quality; "
                    "however, I would verify the trade-off with representative tests."
                ),
            }
            if answer_number == 1:
                payload["workspace"] = workspace
            response = client.post("/api/interview", json=payload)
            assert response.status_code == 200
            assert response.json()["done"] is False

        before_final = response.json()
        assert before_final["progress"]["questionsAsked"] == 8
        assert before_final["progress"]["daysCovered"] >= 4

        final = client.post(
            "/api/interview",
            json={
                "sessionId": "e2e-primary",
                "message": "Final answer: I would document the decision and validate failure modes.",
            },
        )
        assert final.status_code == 200
        assert final.json()["done"] is True
        assert final.json()["reply"] == "Interview completed."
        assert set(final.json()["feedback"]) == {"summary", "strengths", "gaps", "next"}

        second = client.post(
            "/api/interview",
            json={"sessionId": "e2e-secondary", "candidate": candidate("CAND-001")},
        )
        assert second.status_code == 200

    database = Database(database_url)
    try:
        with database.session() as db:
            repository = InterviewSessionRepository(db)
            session = repository.get("e2e-primary")
            assert session is not None
            assert session.status == "completed"
            assert session.question_count == 8
            assert len(set(session.covered_curriculum_days)) >= 4
            assert session.workspace_snapshot["events"][0]["id"] == "evt-e2e-configure"
            assert len(repository.list_turns("e2e-primary")) == 17
    finally:
        database.dispose()

    observations = memory.observations(session_id="e2e-primary", candidate_id="CAND-001")
    assert len(observations) == 8
    assert any("Workspace evidence" in observation.text for observation in observations)
    assert memory.observations(session_id="e2e-secondary", candidate_id="CAND-001") == []
    evaluation_calls = [call for call in provider.calls if call["task"] == "evaluate_answer"]
    assert any(call["context"]["relevant_memories"] for call in evaluation_calls[1:])
