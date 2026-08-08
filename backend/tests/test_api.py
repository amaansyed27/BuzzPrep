from __future__ import annotations

from pathlib import Path
from typing import Sequence

from fastapi.testclient import TestClient

from app.db.database import Database
from app.main import create_app
from app.models.interview import InterviewSession, InterviewTurn
from app.schemas.interview import Feedback
from app.services.interviewer import InterviewEngineResult, InterviewStatePatch
from app.services.session import InterviewSessionRepository

CANDIDATE = {
    "member": {"id": "CAND-001", "name": "Sarah Johnson"},
    "missions": [{"day": 7, "title": "Embeddings Explained", "passed": True, "attempts": 1}],
    "signals": {"commitDays": 28, "missionsCompleted": 30, "missionsFirstTry": 20},
}


def read_session(database_url: str, session_id: str) -> tuple[InterviewSession, list[InterviewTurn]]:
    database = Database(database_url)
    try:
        with database.session() as db:
            repository = InterviewSessionRepository(db)
            session = repository.get(session_id)
            assert session is not None
            turns = repository.list_turns(session_id)
            db.expunge(session)
            for turn in turns:
                db.expunge(turn)
            return session, turns
    finally:
        database.dispose()


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "buzzprep-api"}


def test_create_new_session_persists_candidate_and_initial_state(
    client: TestClient, database_url: str
) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "abc-123", "candidate": CANDIDATE},
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Interview session created. Interview generation is not connected in Issue #1.",
        "done": False,
    }

    session, turns = read_session(database_url, "abc-123")
    assert session.candidate_data == CANDIDATE
    assert session.status == "active"
    assert session.question_count == 0
    assert session.turn_count == 0
    assert session.covered_curriculum_days == []
    assert session.workspace_snapshot == {}
    assert session.structured_scores == {}
    assert session.completion_state == {}
    assert [(turn.role, turn.kind) for turn in turns] == [("interviewer", "placeholder")]


def test_next_http_request_loads_same_session_and_updates_persisted_state(
    client: TestClient, database_url: str
) -> None:
    client.post("/api/interview", json={"sessionId": "same-session", "candidate": CANDIDATE})

    response = client.post(
        "/api/interview",
        json={"sessionId": "same-session", "message": "A vector database stores embeddings."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Response persisted. Interview generation is not connected in Issue #1.",
        "done": False,
    }

    session, turns = read_session(database_url, "same-session")
    assert session.turn_count == 1
    assert session.question_count == 0
    assert [turn.role for turn in turns] == ["interviewer", "candidate", "interviewer"]
    assert turns[1].content == "A vector database stores embeddings."


def test_unknown_session_id_returns_structured_404(client: TestClient) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "missing", "message": "hello"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "session_not_found"


def test_malformed_start_request_returns_structured_422(client: TestClient) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "bad-start", "candidate": {}},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["details"]


def test_malformed_conversation_request_returns_structured_422(client: TestClient) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "bad-turn", "message": "   "},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_request_with_candidate_and_message_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "mixed", "candidate": CANDIDATE, "message": "hello"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_duplicate_session_id_returns_structured_409(client: TestClient) -> None:
    payload = {"sessionId": "duplicate", "candidate": CANDIDATE}
    assert client.post("/api/interview", json=payload).status_code == 200

    response = client.post("/api/interview", json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "session_already_exists"


def test_persistence_survives_separate_app_and_database_instances(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'persistent.db'}"

    with TestClient(create_app(database_url=database_url)) as first_client:
        start_response = first_client.post(
            "/api/interview",
            json={"sessionId": "persistent", "candidate": CANDIDATE},
        )
        assert start_response.status_code == 200

    with TestClient(create_app(database_url=database_url)) as second_client:
        turn_response = second_client.post(
            "/api/interview",
            json={"sessionId": "persistent", "message": "loaded after restart"},
        )
        assert turn_response.status_code == 200

    session, turns = read_session(database_url, "persistent")
    assert session.candidate_data == CANDIDATE
    assert session.turn_count == 1
    assert [turn.content for turn in turns][-2:] == [
        "loaded after restart",
        "Response persisted. Interview generation is not connected in Issue #1.",
    ]


class CompletingTestEngine:
    def start(self, session: InterviewSession) -> InterviewEngineResult:
        return InterviewEngineResult(reply="Test interviewer started.")

    def respond(
        self,
        session: InterviewSession,
        message: str,
        conversation: Sequence[InterviewTurn],
    ) -> InterviewEngineResult:
        return InterviewEngineResult(
            reply="Interview completed.",
            done=True,
            feedback=Feedback(
                summary="Structured test summary.",
                strengths=["Clear explanation"],
                gaps=["Needs more depth"],
                next=["Review retrieval evaluation"],
            ),
            state_patch=InterviewStatePatch(
                question_count=8,
                covered_curriculum_days=[7, 8, 10, 12],
                current_curriculum_day=None,
                current_topic=None,
                current_challenge=None,
                workspace_snapshot={"evidence": ["test-action"]},
                structured_scores={"technical": 0.75},
            ),
        )


def test_engine_state_patch_and_final_response_follow_technical_spec(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'completed.db'}"
    app = create_app(database_url=database_url, interview_engine=CompletingTestEngine())

    with TestClient(app) as test_client:
        start = test_client.post(
            "/api/interview",
            json={"sessionId": "complete-me", "candidate": CANDIDATE},
        )
        assert set(start.json()) == {"reply", "done"}

        response = test_client.post(
            "/api/interview",
            json={"sessionId": "complete-me", "message": "final answer"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "reply": "Interview completed.",
            "done": True,
            "feedback": {
                "summary": "Structured test summary.",
                "strengths": ["Clear explanation"],
                "gaps": ["Needs more depth"],
                "next": ["Review retrieval evaluation"],
            },
        }

        completed_response = test_client.post(
            "/api/interview",
            json={"sessionId": "complete-me", "message": "another answer"},
        )
        assert completed_response.status_code == 409
        assert completed_response.json()["error"]["code"] == "session_completed"

    session, _ = read_session(database_url, "complete-me")
    assert session.status == "completed"
    assert session.completed_at is not None
    assert session.question_count == 8
    assert session.covered_curriculum_days == [7, 8, 10, 12]
    assert session.current_curriculum_day is None
    assert session.current_topic is None
    assert session.current_challenge is None
    assert session.workspace_snapshot == {"evidence": ["test-action"]}
    assert session.structured_scores == {"technical": 0.75}
    assert session.completion_state["feedback"]["summary"] == "Structured test summary."
