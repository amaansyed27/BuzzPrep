from __future__ import annotations

from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.db.database import Database
from app.interview.engine import AdaptiveInterviewEngine, completion_eligible
from app.interview.models import (
    AdaptiveAction,
    AdaptiveDecision,
    GeneratedInterviewQuestion,
)
from app.llm.fake import FakeLLMProvider
from app.llm.gemini import GeminiLLMProvider
from app.main import create_app
from app.services.session import InterviewSessionRepository
from app.profiling.loader import load_candidates


def candidate(candidate_id: str) -> dict:
    record = next(item for item in load_candidates() if item.member.candidate_id == candidate_id)
    return record.model_dump(mode="json", by_alias=True)


def read_session(database_url: str, session_id: str):
    database = Database(database_url)
    try:
        with database.session() as db:
            repository = InterviewSessionRepository(db)
            session = repository.get(session_id)
            turns = repository.list_turns(session_id) if session else []
            if session is not None:
                db.expunge(session)
            for turn in turns:
                db.expunge(turn)
            return session, turns
    finally:
        database.dispose()


def test_hard_completion_gate_is_python_owned() -> None:
    assert completion_eligible(7, [1, 8, 16, 31]) is False
    assert completion_eligible(8, [1, 8, 16]) is False
    assert completion_eligible(8, [1, 8, 16, 31]) is True


def test_fake_finish_requests_cannot_end_interview_early(tmp_path: Path) -> None:
    finish = AdaptiveDecision(action=AdaptiveAction.FINISH, reason="finish now")
    provider = FakeLLMProvider(scripted={"adaptive_decision": [finish] * 8})
    database_url = f"sqlite:///{tmp_path / 'gate.db'}"
    app = create_app(database_url=database_url, interview_engine=AdaptiveInterviewEngine(provider))

    with TestClient(app) as client:
        start = client.post(
            "/api/interview",
            json={"sessionId": "gate", "candidate": candidate("CAND-001")},
        )
        assert start.json()["done"] is False
        for index in range(1, 8):
            response = client.post(
                "/api/interview",
                json={"sessionId": "gate", "message": f"answer {index}"},
            )
            assert response.json()["done"] is False

        before_final, _ = read_session(database_url, "gate")
        assert before_final is not None
        assert before_final.question_count == 8
        assert len(set(before_final.covered_curriculum_days)) >= 4

        final = client.post(
            "/api/interview",
            json={"sessionId": "gate", "message": "answer 8"},
        )
        assert final.status_code == 200
        assert final.json()["done"] is True


def test_finish_request_at_eight_questions_with_only_three_days_is_overridden(tmp_path: Path) -> None:
    finish = AdaptiveDecision(action=AdaptiveAction.FINISH, reason="finish despite missing coverage")
    provider = FakeLLMProvider(scripted={"adaptive_decision": [finish]})
    database_url = f"sqlite:///{tmp_path / 'three-days.db'}"
    app = create_app(database_url=database_url, interview_engine=AdaptiveInterviewEngine(provider))

    with TestClient(app) as client:
        started = client.post(
            "/api/interview",
            json={"sessionId": "three-days", "candidate": candidate("CAND-001")},
        )
        assert started.status_code == 200

        database = Database(database_url)
        try:
            with database.session() as db:
                repository = InterviewSessionRepository(db)
                session = repository.get("three-days")
                assert session is not None
                plan_days = [area["day"] for area in session.completion_state["interviewPlan"]["plan"]]
                session.question_count = 8
                session.covered_curriculum_days = plan_days[:3]
                repository.commit()
        finally:
            database.dispose()

        response = client.post(
            "/api/interview",
            json={"sessionId": "three-days", "message": "please finish now"},
        )
        assert response.status_code == 200
        assert response.json()["done"] is False

    session, _ = read_session(database_url, "three-days")
    assert session is not None
    assert session.question_count == 9
    assert len(set(session.covered_curriculum_days)) == 4


def test_strong_answer_drives_deeper_probe_and_uses_prior_answer(
    client: TestClient, fake_provider: FakeLLMProvider
) -> None:
    client.post(
        "/api/interview",
        json={"sessionId": "strong", "candidate": candidate("CAND-001")},
    )
    answer = "I would choose this because it reduces latency, however the trade-off is higher memory use."
    response = client.post(
        "/api/interview",
        json={"sessionId": "strong", "message": answer},
    )

    assert response.status_code == 200
    assert "You said" in response.json()["reply"]
    assert "constraint" in response.json()["reply"]
    generate_calls = [call for call in fake_provider.calls if call["task"] == "generate_question"]
    assert generate_calls[-1]["context"]["candidate_answer"] == answer
    assert generate_calls[-1]["context"]["adaptive_decision"]["action"] == "deepen"


def test_weak_answer_drives_targeted_diagnostic_probe(client: TestClient) -> None:
    client.post(
        "/api/interview",
        json={"sessionId": "weak", "candidate": candidate("CAND-001")},
    )
    response = client.post(
        "/api/interview",
        json={"sessionId": "weak", "message": "not sure"},
    )

    assert response.status_code == 200
    assert "Clarify" in response.json()["reply"]
    assert "prerequisite" in response.json()["reply"]


def test_workspace_evidence_is_validated_and_can_drive_truthful_follow_up(
    client: TestClient, database_url: str
) -> None:
    client.post(
        "/api/interview",
        json={"sessionId": "workspace", "candidate": candidate("CAND-001")},
    )
    workspace = {
        "nodes": [],
        "edges": [],
        "config": {"top_k": 4},
        "editors": {},
        "submissions": [],
        "events": [
            {
                "id": "evt-1",
                "type": "connect",
                "timestamp": "2026-08-09T00:00:00Z",
                "payload": {"edgeId": "e1", "source": "retriever", "target": "reranker"},
            }
        ],
        "workspaceActive": True,
        "challengeId": "challenge-1",
        "selection": {"nodeIds": ["ui-only"], "edgeIds": []},
    }
    response = client.post(
        "/api/interview",
        json={
            "sessionId": "workspace",
            "message": "I connected the stages to improve relevance.",
            "workspace": workspace,
        },
    )

    assert response.status_code == 200
    assert "connected retriever to reranker" in response.json()["reply"]
    session, turns = read_session(database_url, "workspace")
    assert session is not None
    assert "selection" not in session.workspace_snapshot
    assert turns[-2].payload["workspace"]["events"][0]["type"] == "connect"


def test_no_workspace_claim_is_generated_when_workspace_absent(client: TestClient) -> None:
    client.post(
        "/api/interview",
        json={"sessionId": "no-workspace", "candidate": candidate("CAND-001")},
    )
    response = client.post(
        "/api/interview",
        json={"sessionId": "no-workspace", "message": "I would validate the behavior with tests."},
    )
    assert "You connected" not in response.json()["reply"]
    assert "reset the workspace" not in response.json()["reply"]


def test_malformed_workspace_is_a_structured_422(client: TestClient) -> None:
    response = client.post(
        "/api/interview",
        json={
            "sessionId": "bad-workspace",
            "candidate": candidate("CAND-001"),
            "workspace": {"nodes": "not-a-list"},
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_sparse_candidate_covers_exact_four_demonstrated_days_before_finish(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'sparse.db'}"
    app = create_app(
        database_url=database_url,
        interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
    )
    with TestClient(app) as client:
        client.post(
            "/api/interview",
            json={"sessionId": "sparse", "candidate": candidate("CAND-016")},
        )
        for index in range(1, 8):
            response = client.post(
                "/api/interview",
                json={"sessionId": "sparse", "message": f"candidate answer {index}"},
            )
            assert response.json()["done"] is False

        session, _ = read_session(database_url, "sparse")
        assert session is not None
        assert session.question_count == 8
        assert set(session.covered_curriculum_days) == {1, 8, 16, 31}
        assert not ({7, 12, 22} & set(session.covered_curriculum_days))

        final = client.post(
            "/api/interview",
            json={"sessionId": "sparse", "message": "candidate answer 8"},
        )
        assert final.json()["done"] is True
        assert set(final.json()["feedback"]) == {"summary", "strengths", "gaps", "next"}


def test_invalid_structured_output_rolls_back_candidate_turn(tmp_path: Path) -> None:
    provider = FakeLLMProvider(scripted={"evaluate_answer": [{"strength": "impossible"}]})
    database_url = f"sqlite:///{tmp_path / 'invalid-output.db'}"
    app = create_app(database_url=database_url, interview_engine=AdaptiveInterviewEngine(provider))

    with TestClient(app) as client:
        start = client.post(
            "/api/interview",
            json={"sessionId": "invalid-output", "candidate": candidate("CAND-001")},
        )
        assert start.status_code == 200
        before, turns_before = read_session(database_url, "invalid-output")
        assert before is not None

        failed = client.post(
            "/api/interview",
            json={"sessionId": "invalid-output", "message": "this must roll back"},
        )
        assert failed.status_code == 503
        assert failed.json()["error"]["code"] == "llm_provider_error"

    after, turns_after = read_session(database_url, "invalid-output")
    assert after is not None and before is not None
    assert after.question_count == before.question_count == 1
    assert after.turn_count == before.turn_count == 0
    assert len(turns_after) == len(turns_before) == 1


def test_live_provider_missing_configuration_is_controlled_and_does_not_create_session(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'missing-key.db'}"
    provider = GeminiLLMProvider(api_key=None, model=None)
    app = create_app(database_url=database_url, interview_engine=AdaptiveInterviewEngine(provider))

    with TestClient(app) as client:
        response = client.post(
            "/api/interview",
            json={"sessionId": "missing-key", "candidate": candidate("CAND-001")},
        )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "llm_provider_error"
        assert "LLM_API_KEY" in response.json()["error"]["message"]

    session, turns = read_session(database_url, "missing-key")
    assert session is None
    assert turns == []


def test_gemini_adapter_sends_json_schema_and_validates_response() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured.update(json.loads(request.content.decode()))
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"question":"Why this design?","kind":"initial",'
                                        '"challenge_summary":null,"workspace_fact_used":null}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        provider = GeminiLLMProvider(
            api_key="test-key",
            model="gemini-test-model",
            client=http_client,
        )
        result = provider.generate_structured(
            task="generate_question",
            system_prompt="system",
            context={"planned_area": {"day": 1}},
            output_schema=GeneratedInterviewQuestion,
        )

    assert result.question == "Why this design?"
    response_format = captured["generationConfig"]["responseFormat"]["text"]
    assert response_format["mimeType"] == "application/json"
    assert response_format["schema"]["type"] == "object"
