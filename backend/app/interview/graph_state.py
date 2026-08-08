from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypedDict

from app.interview.models import AdaptiveDecision, TurnEvaluation
from app.models.interview import InterviewSession, InterviewTurn
from app.planning.models import InterviewPlan, PlannedArea
from app.profiling.candidate import CandidateProfile
from app.schemas.workspace import SerializedWorkspace
from app.services.interviewer import InterviewEngineResult


class InterviewGraphState(TypedDict, total=False):
    mode: Literal["start", "respond"]
    session: InterviewSession
    conversation: Sequence[InterviewTurn]
    candidate_answer: str
    workspace: SerializedWorkspace | None
    workspace_facts: list[str]
    profile: CandidateProfile
    plan: InterviewPlan
    current_area: PlannedArea
    evaluation: TurnEvaluation
    adaptive_decision: AdaptiveDecision
    completion_eligible: bool
    result: InterviewEngineResult
