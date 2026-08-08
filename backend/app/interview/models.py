from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AnswerStrength(StrEnum):
    STRONG = "strong"
    ADEQUATE = "adequate"
    WEAK = "weak"
    UNCLEAR = "unclear"


class WorkspaceConsistency(StrEnum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    UNCLEAR = "unclear"
    NOT_APPLICABLE = "not_applicable"


class AdaptiveAction(StrEnum):
    FOLLOW_UP = "follow_up"
    DEEPEN = "deepen"
    TRANSITION = "transition"
    FINISH = "finish"


class QuestionKind(StrEnum):
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    DEEPER = "deeper"
    TRANSITION = "transition"
    DIAGNOSTIC = "diagnostic"


class GeneratedInterviewQuestion(BaseModel):
    question: str = Field(min_length=1)
    kind: QuestionKind
    challenge_summary: str | None = None
    workspace_fact_used: str | None = None


class TurnEvaluation(BaseModel):
    strength: AnswerStrength
    correctness: float = Field(ge=0.0, le=1.0)
    reasoning_quality: float = Field(ge=0.0, le=1.0)
    trade_off_awareness: float = Field(ge=0.0, le=1.0)
    practical_understanding: float = Field(ge=0.0, le=1.0)
    workspace_consistency: WorkspaceConsistency
    missing_points: list[str] = Field(default_factory=list)
    follow_up_recommendation: str = Field(min_length=1)


class AdaptiveDecision(BaseModel):
    action: AdaptiveAction
    reason: str = Field(min_length=1)
    focus: str | None = None
    constraint: str | None = None


class FinalFeedbackOutput(BaseModel):
    summary: str = Field(min_length=1)
    strengths: list[str]
    gaps: list[str]
    next: list[str]
