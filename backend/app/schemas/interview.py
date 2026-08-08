from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class InterviewRequest(BaseModel):
    sessionId: str = Field(min_length=1, max_length=255)
    candidate: dict[str, Any] | None = None
    message: str | None = None

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
        if self.candidate is not None and not self.candidate:
            raise ValueError("candidate must be a non-empty object")
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


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Feedback | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
