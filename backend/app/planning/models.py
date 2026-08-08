from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.planning.interactions import InteractionType
from app.profiling.candidate import ExperienceLevel

MINIMUM_DAYS = 4
MINIMUM_QUESTIONS = 8
QUESTIONS_PER_AREA = 2


class PlanIntent(StrEnum):
    ASSESSMENT = "assessment"
    DIAGNOSTIC = "diagnostic"
    GAP_CHECK = "gap_check"
    EXPLORATORY = "exploratory"


class Difficulty(StrEnum):
    INTRODUCTORY = "introductory"
    STANDARD = "standard"
    ADVANCED = "advanced"


class PlannerProfileSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    experience_level: ExperienceLevel = Field(alias="experienceLevel")
    strong_days: list[int] = Field(alias="strongDays")
    weaker_days: list[int] = Field(alias="weakerDays")
    failed_days: list[int] = Field(alias="failedDays")
    skipped_days: list[int] = Field(alias="skippedDays")
    first_try_rate: float = Field(alias="firstTryRate")
    commit_days: int = Field(alias="commitDays")


class PlannedArea(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    day: int = Field(ge=1, le=31)
    module: str
    topic: str
    activity_type: str = Field(alias="activityType")
    intent: PlanIntent
    difficulty: Difficulty
    objectives: list[str]
    tools: list[str]
    interaction_types: list[InteractionType] = Field(alias="interactionTypes", min_length=1)
    evidence_to_look_for: list[str] = Field(alias="evidenceToLookFor", min_length=1)
    reason_selected: str = Field(alias="reasonSelected", min_length=1)
    question_budget: int = Field(default=QUESTIONS_PER_AREA, alias="questionBudget", ge=1)


class InterviewPlan(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    candidate_id: str = Field(alias="candidateId")
    profile: PlannerProfileSummary
    plan: list[PlannedArea] = Field(min_length=MINIMUM_DAYS)
    minimum_questions: int = Field(
        default=MINIMUM_QUESTIONS, alias="minimumQuestions", ge=MINIMUM_QUESTIONS
    )
    minimum_days: int = Field(default=MINIMUM_DAYS, alias="minimumDays", ge=MINIMUM_DAYS)
    planned_questions: int = Field(alias="plannedQuestions", ge=MINIMUM_QUESTIONS)
