from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator


app = FastAPI(title="BuzzPrep API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterviewRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    candidate: dict[str, Any] | None = None
    message: str | None = None

    @model_validator(mode="after")
    def validate_turn(self) -> "InterviewRequest":
        if self.candidate is None and self.message is None:
            raise ValueError("Provide candidate when starting or message for a conversation turn")
        return self


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool = False
    feedback: Feedback | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "buzzprep-api"}


@app.post("/api/interview", response_model=InterviewResponse)
def interview(payload: InterviewRequest) -> InterviewResponse:
    """Hackathon API contract scaffold.

    The adaptive interviewer, persistence, LLM evaluation, Breeth memory, and
    workspace-action handling will be connected in subsequent issues.
    """
    if payload.candidate is not None:
        name = payload.candidate.get("member", {}).get("name", "candidate")
        return InterviewResponse(
            reply=(
                f"Welcome, {name}. BuzzPrep is ready to begin. "
                "The adaptive interview engine is not connected in this scaffold yet."
            )
        )

    return InterviewResponse(
        reply=(
            "Your response reached the BuzzPrep API scaffold. "
            "Adaptive follow-up generation is not connected yet."
        )
    )
