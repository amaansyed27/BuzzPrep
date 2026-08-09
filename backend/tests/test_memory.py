from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from app.interview.engine import AdaptiveInterviewEngine
from app.llm.fake import FakeLLMProvider
from app.main import create_app
from app.memory.base import MemoryObservation
from app.memory.breeth import BreethMemoryService
from app.memory.fake import InMemoryMemoryService
from app.profiling.loader import load_candidates


def candidate(candidate_id: str = "CAND-001") -> dict[str, Any]:
    record = next(item for item in load_candidates() if item.member.candidate_id == candidate_id)
    return record.model_dump(mode="json", by_alias=True)


def test_breeth_adapter_scopes_write_and_retrieval_by_session_and_candidate() -> None:
    created: list[Any] = []

    class CapturingClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.writes: list[tuple[str, dict[str, Any]]] = []
            self.retrievals: list[tuple[str, dict[str, Any]]] = []
            created.append(self)

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def write(self, content: str, **kwargs: Any) -> None:
            self.writes.append((content, kwargs))

        def retrieve(self, query: str, **kwargs: Any):
            self.retrievals.append((query, kwargs))
            return SimpleNamespace(edges=[SimpleNamespace(fact="Candidate justified retry boundaries")])

    service = BreethMemoryService(api_key="test-key", client_factory=CapturingClient)
    observation = MemoryObservation(
        day=16,
        turn_number=4,
        source="answer_and_workspace",
        text="Candidate configured timeout handling and justified retry boundaries.",
    )

    service.write_observation(
        session_id="session-a",
        candidate_id="CAND-001",
        observation=observation,
    )
    records = service.retrieve_relevant(
        session_id="session-a",
        candidate_id="CAND-001",
        query="retry boundaries",
    )

    assert len(created) == 2
    assert all(client.kwargs["end_user_id"] == "CAND-001" for client in created)
    assert created[0].writes[0][1]["group_id"] == "session-a"
    assert created[1].retrievals[0][1]["group_id"] == "session-a"
    assert records[0].text == "Candidate justified retry boundaries"


def test_in_memory_service_prevents_cross_session_and_candidate_leakage() -> None:
    service = InMemoryMemoryService()
    observation = MemoryObservation(
        day=8,
        turn_number=1,
        source="answer",
        text="Candidate explained cosine similarity but missed recall latency trade-offs.",
    )
    service.write_observation(
        session_id="session-a",
        candidate_id="CAND-001",
        observation=observation,
    )

    assert service.retrieve_relevant(
        session_id="session-a",
        candidate_id="CAND-001",
        query="cosine similarity",
    )
    assert service.retrieve_relevant(
        session_id="session-b",
        candidate_id="CAND-001",
        query="cosine similarity",
    ) == []
    assert service.retrieve_relevant(
        session_id="session-a",
        candidate_id="CAND-002",
        query="cosine similarity",
    ) == []


def test_memory_failure_is_non_fatal_for_interview_and_sql_state(
    tmp_path: Path,
    caplog,
) -> None:
    class FailingMemoryService:
        def write_observation(self, **kwargs: Any) -> None:
            raise TimeoutError("memory unavailable")

        def retrieve_relevant(self, **kwargs: Any):
            raise TimeoutError("memory unavailable")

    memory = FailingMemoryService()
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'memory-failure.db'}",
        interview_engine=AdaptiveInterviewEngine(FakeLLMProvider(), memory),
        memory_service=memory,
    )

    with caplog.at_level(logging.WARNING), TestClient(app) as client:
        start = client.post(
            "/api/interview",
            json={"sessionId": "memory-down", "candidate": candidate()},
        )
        turn = client.post(
            "/api/interview",
            json={"sessionId": "memory-down", "message": "I would validate this with tests."},
        )

    assert start.status_code == 200
    assert turn.status_code == 200
    assert turn.json()["progress"]["questionsAsked"] == 2
    assert "memory retrieval failed" in caplog.text
    assert "memory write failed" in caplog.text
