from __future__ import annotations

import re
from collections import defaultdict

from app.memory.base import MemoryObservation, MemoryRecord


def _terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9_]+", value.lower()) if len(term) >= 4}


class InMemoryMemoryService:
    """Deterministic session- and candidate-scoped memory for tests and local demos."""

    def __init__(self) -> None:
        self._observations: defaultdict[tuple[str, str], list[MemoryObservation]] = defaultdict(list)

    def write_observation(
        self,
        *,
        session_id: str,
        candidate_id: str,
        observation: MemoryObservation,
    ) -> None:
        self._observations[(candidate_id, session_id)].append(observation.model_copy(deep=True))

    def retrieve_relevant(
        self,
        *,
        session_id: str,
        candidate_id: str,
        query: str,
        limit: int = 4,
    ) -> list[MemoryRecord]:
        observations = self._observations.get((candidate_id, session_id), [])
        query_terms = _terms(query)
        ranked = sorted(
            enumerate(observations),
            key=lambda item: (len(query_terms & _terms(item[1].text)), item[0]),
            reverse=True,
        )
        return [MemoryRecord(text=observation.text) for _, observation in ranked[: max(0, limit)]]

    def observations(self, *, session_id: str, candidate_id: str) -> list[MemoryObservation]:
        return [
            observation.model_copy(deep=True)
            for observation in self._observations.get((candidate_id, session_id), [])
        ]
