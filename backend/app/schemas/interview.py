from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.workspace import SerializedWorkspace


class IntegrityTelemetryEvent(BaseModel):
    """Transparent focus telemetry kept separate from semantic answer evidence."""

    type: Literal[
        "tab_hidden",
        "tab_visible",
        "window_blur",
        "window_focus",
        "fullscreen_enter",
        "fullscreen_exit",
        "reconnect",
    ]
    timestamp: datetime


class InterviewRequest(BaseModel):
    sessionId: str = Field(min_length=1, max_length=255)
    candidate: dict[str, Any] | None = None
    message: str | None = None
    workspace: SerializedWorkspace | None = None
    integrityEvents: list[IntegrityTelemetryEvent] = Field(default_factory=list, max_length=100)

    @field_validator("sessionId")
    @classmethod
    def normalize_session_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("sessionId must not be blank")
        return value

    @model_validator(mode="after")
    def validate_request_kind(self) -> InterviewRequest:
        is_start = self.candidate is not None
        is_turn = self.message is not None

        if is_start == is_turn:
            raise ValueError("Provide exactly one of candidate or message")
        if self.message is not None and not self.message.strip():
            raise ValueError("message must not be blank")
        return self

    @property
    def is_start(self) -> bool:
        return self.candidate is not None


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class ChallengeMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    curriculum_day: int = Field(alias="curriculumDay", ge=1, le=31)
    topic: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    difficulty: str = Field(min_length=1)
    interaction_types: list[str] = Field(alias="interactionTypes", min_length=1)
    question_kind: str = Field(alias="questionKind", min_length=1)
    challenge_summary: str | None = Field(default=None, alias="challengeSummary")


class InterviewProgress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    questions_asked: int = Field(alias="questionsAsked", ge=0)
    minimum_questions: int = Field(alias="minimumQuestions", ge=1)
    days_covered: int = Field(alias="daysCovered", ge=0)
    minimum_days: int = Field(alias="minimumDays", ge=1)


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Feedback | None = None
    challenge: ChallengeMetadata | None = None
    progress: InterviewProgress | None = None


class InterviewHistoryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    status: Literal["active", "completed"]
    candidate_name: str = Field(alias="candidateName")
    candidate_role: str = Field(alias="candidateRole")
    created_at: datetime = Field(alias="createdAt")
    last_activity: datetime = Field(alias="lastActivity")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    questions_asked: int = Field(alias="questionsAsked", ge=0)
    days_covered: int = Field(alias="daysCovered", ge=0)
    current_topic: str | None = Field(default=None, alias="currentTopic")
    result_available: bool = Field(alias="resultAvailable")


class InterviewHistoryList(BaseModel):
    interviews: list[InterviewHistoryItem]


class InterviewTranscriptMessage(BaseModel):
    sequence: int
    role: Literal["interviewer", "candidate"]
    text: str


class InterviewHistoryDetail(InterviewHistoryItem):
    candidate: dict[str, Any]
    challenge: ChallengeMetadata | None = None
    progress: InterviewProgress
    feedback: Feedback | None = None
    messages: list[InterviewTranscriptMessage]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
