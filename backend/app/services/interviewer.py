from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Any, Protocol

from pydantic import BaseModel, Field, model_validator

from app.models.interview import InterviewSession, InterviewTurn
from app.schemas.interview import Feedback
from app.schemas.workspace import SerializedWorkspace


class InterviewEngineError(Exception):
    status_code = 500
    code = "interview_engine_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InterviewProviderError(InterviewEngineError):
    status_code = 503
    code = "llm_provider_error"


class InterviewInputError(InterviewEngineError):
    status_code = 422
    code = "invalid_candidate"


class InterviewStatePatch(BaseModel):
    """Validated deterministic state changes an interview engine may request."""

    question_count: int | None = Field(default=None, ge=0)
    covered_curriculum_days: list[Annotated[int, Field(ge=1, le=31)]] | None = None
    current_curriculum_day: int | None = Field(default=None, ge=1, le=31)
    current_topic: str | None = None
    current_challenge: dict[str, Any] | None = None
    workspace_snapshot: dict[str, Any] | None = None
    structured_scores: dict[str, Any] | None = None
    completion_state: dict[str, Any] | None = None


class InterviewEngineResult(BaseModel):
    reply: str = Field(min_length=1)
    done: bool = False
    feedback: Feedback | None = None
    state_patch: InterviewStatePatch = Field(default_factory=InterviewStatePatch)
    turn_kind: str = "message"
    turn_payload: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_feedback(self) -> InterviewEngineResult:
        if self.done and self.feedback is None:
            raise ValueError("A completed interview engine result must include feedback")
        if not self.done and self.feedback is not None:
            raise ValueError("Feedback may only be returned when done is true")
        return self


class InterviewEngine(Protocol):
    def start(
        self,
        session: InterviewSession,
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult: ...

    def respond(
        self,
        session: InterviewSession,
        message: str,
        conversation: Sequence[InterviewTurn],
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult: ...


class PlaceholderInterviewEngine:
    """Legacy boundary implementation retained for explicit tests or diagnostics."""

    def start(
        self,
        session: InterviewSession,
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult:
        return InterviewEngineResult(
            reply="Interview session created. Interview generation is not connected.",
            turn_kind="placeholder",
        )

    def respond(
        self,
        session: InterviewSession,
        message: str,
        conversation: Sequence[InterviewTurn],
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult:
        return InterviewEngineResult(
            reply="Response persisted. Interview generation is not connected.",
            turn_kind="placeholder",
        )
