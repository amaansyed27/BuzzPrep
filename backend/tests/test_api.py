from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from fastapi.testclient import TestClient

from app.db.database import Database
from app.interview.engine import AdaptiveInterviewEngine
from app.llm.fake import FakeLLMProvider
from app.main import create_app
from app.models.interview import InterviewSession, InterviewTurn
from app.schemas.interview import Feedback
from app.schemas.workspace import SerializedWorkspace
from app.services.interviewer import InterviewEngineResult, InterviewStatePatch
from app.services.session import InterviewSessionRepository

CANDIDATE = {
    "member": {
        "id": "CAND-001",
        "name": "Sarah Johnson",
        "jobRole": "Senior Data Engineer",
        "yearsExperience": 9,
        "education": "MS Computer Science",
        "status": "COMPLETED",
    },
    "missions": [
        {"day": 7, "title": "Embeddings Explained", "passed": True, "attempts": 1},
        {"day": 8, "title": "Vector Databases Overview", "passed": True, "attempts": 1},
        {"day": 10, "title": "The Retrieval & Matching Engine", "passed": True, "attempts": 2},
        {"day": 16, "title": "Chatbot Backend & API Integration", "passed": True, "attempts": 1},
    ],
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


def test_create_new_session_emits_and_persists_first_question(
    client: TestClient, database_url: str
) -> None:
    response = client.post(
        "/api/interview",
        json={"sessionId": "abc-123", "candidate": CANDIDATE},
    )

    assert response.status_code == 200
    assert response.json()["done"] is False
    assert "Day" in response.json()["reply"]
    assert response.json()["challenge"]["curriculumDay"] >= 1
    assert response.json()["challenge"]["interactionTypes"]
    assert response.json()["progress"] == {
        "questionsAsked": 1,
        "minimumQuestions": 8,
        "daysCovered": 1,
        "minimumDays": 4,
    }

    session, turns = read_session(database_url, "abc-123")
    assert session.candidate_data == CANDIDATE
    assert session.status == "active"
    assert session.question_count == 1
    assert len(session.covered_curriculum_days) == 1
    assert session.current_curriculum_day in session.covered_curriculum_days
    assert session.current_topic
    assert session.completion_state["candidateProfile"]["candidate_id"] == "CAND-001"
    plan_days = {area["day"] for area in session.completion_state["interviewPlan"]["plan"]}
    assert len(plan_days) >= 4
    assert session.current_curriculum_day in plan_days
    assert [(turn.role, turn.kind) for turn in turns] == [("interviewer", "question")]


def test_next_http_request_loads_same_session_and_updates_persisted_state(
    client: TestClient, database_url: str
) -> None:
    client.post("/api/interview", json={"sessionId": "same-session", "candidate": CANDIDATE})

    response = client.post(
        "/api/interview",
        json={
            "sessionId": "same-session",
            "message": "I would use a vector database because semantic similarity matters, with a trade-off in operational cost.",
        },
    )

    assert response.status_code == 200
    assert response.json()["done"] is False
    assert "You said" in response.json()["reply"]

    session, turns = read_session(database_url, "same-session")
    assert session.turn_count == 1
    assert session.question_count == 2
    assert [turn.role for turn in turns] == ["interviewer", "candidate", "interviewer"]
    assert turns[1].content.startswith("I would use a vector database")
    assert session.structured_scores["turnEvaluations"][0]["strength"] == "strong"


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
    assert response.json()["error"]["code"] == "invalid_request"


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

    with TestClient(
        create_app(
            database_url=database_url,
            interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
        )
    ) as first_client:
        start_response = first_client.post(
            "/api/interview",
            json={"sessionId": "persistent", "candidate": CANDIDATE},
        )
        assert start_response.status_code == 200

    with TestClient(
        create_app(
            database_url=database_url,
            interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
        )
    ) as second_client:
        turn_response = second_client.post(
            "/api/interview",
            json={"sessionId": "persistent", "message": "loaded after restart with enough context"},
        )
        assert turn_response.status_code == 200

    session, turns = read_session(database_url, "persistent")
    assert session.candidate_data == CANDIDATE
    assert session.turn_count == 1
    assert session.question_count == 2
    assert turns[-2].content == "loaded after restart with enough context"
    assert turns[-1].kind == "question"


class CompletingTestEngine:
    def start(
        self,
        session: InterviewSession,
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult:
        return InterviewEngineResult(reply="Test interviewer started.")

    def respond(
        self,
        session: InterviewSession,
        message: str,
        conversation: Sequence[InterviewTurn],
        *,
        workspace: SerializedWorkspace | None = None,
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


def test_engine_state_patch_and_final_response_follow_technical_spec(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'completed.db'}"
    app = create_app(database_url=database_url, interview_engine=CompletingTestEngine())

    with TestClient(app) as test_client:
        start = test_client.post(
            "/api/interview",
            json={"sessionId": "complete-me", "candidate": CANDIDATE},
        )
        assert start.json() == {
            "reply": "Test interviewer started.",
            "done": False,
            "progress": {
                "questionsAsked": 0,
                "minimumQuestions": 8,
                "daysCovered": 0,
                "minimumDays": 4,
            },
        }

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
            "progress": {
                "questionsAsked": 8,
                "minimumQuestions": 8,
                "daysCovered": 4,
                "minimumDays": 4,
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
    assert session.workspace_snapshot == {"evidence": ["test-action"]}
    assert session.structured_scores == {"technical": 0.75}
    assert session.completion_state["feedback"]["summary"] == "Structured test summary."
