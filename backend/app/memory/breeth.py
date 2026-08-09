from __future__ import annotations

from collections.abc import Callable
from typing import Any

from breeth import BreethClient

from app.memory.base import MemoryObservation, MemoryRecord


class BreethMemoryService:
    """Small production adapter around Breeth's official synchronous Python SDK."""

    def __init__(
        self,
        *,
        api_key: str,
        timeout_seconds: float = 10.0,
        client_factory: Callable[..., Any] = BreethClient,
    ) -> None:
        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds
        self.client_factory = client_factory

    def _client(self, candidate_id: str):
        return self.client_factory(
            api_key=self.api_key,
            end_user_id=candidate_id,
            timeout=self.timeout_seconds,
        )

    def write_observation(
        self,
        *,
        session_id: str,
        candidate_id: str,
        observation: MemoryObservation,
    ) -> None:
        content = (
            f"Day {observation.day}: {observation.text}\n"
            f"Evidence: {observation.source}, answer turn {observation.turn_number}."
        )
        with self._client(candidate_id) as client:
            client.write(
                content,
                group_id=session_id,
                source_description="buzzprep_interview_evidence",
            )

    def retrieve_relevant(
        self,
        *,
        session_id: str,
        candidate_id: str,
        query: str,
        limit: int = 4,
    ) -> list[MemoryRecord]:
        with self._client(candidate_id) as client:
            response = client.retrieve(query, group_id=session_id, limit=limit)
        return [MemoryRecord(text=edge.fact) for edge in response.edges if edge.fact.strip()]
