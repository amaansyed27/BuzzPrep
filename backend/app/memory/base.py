from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, Field


class MemoryObservation(BaseModel):
    day: int = Field(ge=1, le=31)
    turn_number: int = Field(ge=1)
    source: Literal["answer", "workspace", "answer_and_workspace"]
    text: str = Field(min_length=1, max_length=2000)


class MemoryRecord(BaseModel):
    text: str = Field(min_length=1)


class MemoryService(Protocol):
    def write_observation(
        self,
        *,
        session_id: str,
        candidate_id: str,
        observation: MemoryObservation,
    ) -> None: ...

    def retrieve_relevant(
        self,
        *,
        session_id: str,
        candidate_id: str,
        query: str,
        limit: int = 4,
    ) -> list[MemoryRecord]: ...


class NoopMemoryService:
    def write_observation(
        self,
        *,
        session_id: str,
        candidate_id: str,
        observation: MemoryObservation,
    ) -> None:
        return None

    def retrieve_relevant(
        self,
        *,
        session_id: str,
        candidate_id: str,
        query: str,
        limit: int = 4,
    ) -> list[MemoryRecord]:
        return []
