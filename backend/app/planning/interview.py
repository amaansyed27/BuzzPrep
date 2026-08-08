from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.curriculum.models import CurriculumCatalog, CurriculumDay
from app.planning.interactions import InteractionType, interactions_for_day
from app.profiling.candidate import (
    CandidateProfile,
    ExperienceLevel,
    MissionSignal,
    MissionState,
)

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


_ROLE_MODULE_RULES: tuple[tuple[tuple[str, ...], tuple[int, ...]], ...] = (
    (("devops", "site reliability", "cloud"), (7, 8, 5)),
    (("data",), (2, 3, 4, 7, 8)),
    (("ai engineer", "machine learning", "ml engineer"), (3, 4, 6, 7, 8)),
    (("architect", "distinguished", "principal"), (6, 7, 8, 5)),
    (("intern", "junior"), (1, 2, 3, 4, 5)),
    (("backend", "software engineer", "developer", "legacy systems"), (5, 6, 7, 8, 3)),
    (("business", "marketing", "human resources", "hr manager", "ux"), (1, 2, 4, 5)),
    (("it support",), (1, 5, 7, 8)),
)


def _preferred_modules(job_role: str) -> tuple[int, ...]:
    normalized = job_role.lower()
    for terms, modules in _ROLE_MODULE_RULES:
        if any(term in normalized for term in terms):
            return modules
    return ()


def _difficulty(profile: CandidateProfile, mission: MissionSignal | None) -> Difficulty:
    if mission is None or mission.state is not MissionState.PASSED:
        return Difficulty.INTRODUCTORY
    if mission.attempts >= 4:
        return Difficulty.INTRODUCTORY
    if (
        profile.experience_level is ExperienceLevel.INTRODUCTORY
        and mission.attempts >= 2
    ):
        return Difficulty.INTRODUCTORY
    if profile.years_experience <= 1 and mission.attempts >= 2:
        return Difficulty.INTRODUCTORY
    if mission.attempts >= 2:
        return Difficulty.STANDARD
    if profile.experience_level is ExperienceLevel.ADVANCED:
        return Difficulty.ADVANCED
    if profile.technical_role and profile.first_try_rate >= 0.75:
        return Difficulty.ADVANCED
    return Difficulty.STANDARD


def _intent(mission: MissionSignal | None) -> PlanIntent:
    if mission is None:
        return PlanIntent.EXPLORATORY
    if mission.state is MissionState.PASSED:
        return PlanIntent.ASSESSMENT
    if mission.state is MissionState.FAILED:
        return PlanIntent.DIAGNOSTIC
    return PlanIntent.GAP_CHECK


def _signal_rank(signal: MissionSignal) -> tuple[int, int]:
    if signal.state is MissionState.PASSED and signal.attempts >= 3:
        return (0, -signal.attempts)
    if signal.state is MissionState.PASSED and signal.attempts == 1:
        return (1, 0)
    return (2, -signal.attempts)


def _pick_best(
    candidates: list[MissionSignal],
    catalog: CurriculumCatalog,
    selected: list[MissionSignal],
    preferred_modules: tuple[int, ...],
) -> MissionSignal | None:
    if not candidates:
        return None
    selected_modules = {catalog.day(signal.day).module_number for signal in selected}
    preferred = set(preferred_modules)
    return min(
        candidates,
        key=lambda signal: (
            catalog.day(signal.day).module_number in selected_modules,
            catalog.day(signal.day).module_number not in preferred,
            _signal_rank(signal),
            -signal.day,
        ),
    )


def _select_passed_days(
    profile: CandidateProfile,
    catalog: CurriculumCatalog,
    target_days: int,
) -> list[MissionSignal]:
    passed = [signal for signal in profile.mission_signals if signal.state is MissionState.PASSED]
    if len(passed) <= target_days:
        return sorted(passed, key=lambda signal: signal.day)

    preferred_modules = _preferred_modules(profile.job_role)
    selected: list[MissionSignal] = []

    weak = [signal for signal in passed if signal.attempts >= 3]
    weak_pick = _pick_best(weak, catalog, selected, preferred_modules)
    if weak_pick is not None:
        selected.append(weak_pick)

    strong = [signal for signal in passed if signal.attempts == 1 and signal not in selected]
    strong_pick = _pick_best(strong, catalog, selected, preferred_modules)
    if strong_pick is not None and len(selected) < target_days:
        selected.append(strong_pick)

    role_relevant = [
        signal
        for signal in passed
        if signal not in selected and catalog.day(signal.day).module_number in preferred_modules
    ]
    role_pick = _pick_best(role_relevant, catalog, selected, preferred_modules)
    if role_pick is not None and len(selected) < target_days:
        selected.append(role_pick)

    while len(selected) < target_days:
        remaining = [signal for signal in passed if signal not in selected]
        pick = _pick_best(remaining, catalog, selected, preferred_modules)
        if pick is None:
            break
        selected.append(pick)

    return sorted(selected, key=lambda signal: signal.day)


def _fallback_selections(
    profile: CandidateProfile,
    catalog: CurriculumCatalog,
    selected: list[MissionSignal],
    target_days: int,
) -> list[tuple[int, MissionSignal | None]]:
    chosen: list[tuple[int, MissionSignal | None]] = [
        (signal.day, signal) for signal in selected
    ]
    chosen_days = {signal.day for signal in selected}
    preferred_modules = _preferred_modules(profile.job_role)

    for state in (MissionState.FAILED, MissionState.SKIPPED):
        while len(chosen) < target_days:
            state_candidates = [
                signal
                for signal in profile.mission_signals
                if signal.state is state and signal.day not in chosen_days
            ]
            picked_signals = [signal for _, signal in chosen if signal is not None]
            pick = _pick_best(state_candidates, catalog, picked_signals, preferred_modules)
            if pick is None:
                break
            chosen.append((pick.day, pick))
            chosen_days.add(pick.day)

    if len(chosen) >= target_days:
        return chosen

    observed_days = [signal.day for signal in profile.mission_signals]
    progression_ceiling = max(observed_days, default=1)
    exploratory_limit = max(progression_ceiling, target_days)
    for curriculum_day in catalog.days:
        if len(chosen) >= target_days:
            break
        if curriculum_day.day > exploratory_limit or curriculum_day.day in chosen_days:
            continue
        chosen.append((curriculum_day.day, None))
        chosen_days.add(curriculum_day.day)

    if len(chosen) < target_days:
        for curriculum_day in catalog.days:
            if curriculum_day.day in chosen_days:
                continue
            chosen.append((curriculum_day.day, None))
            chosen_days.add(curriculum_day.day)
            if len(chosen) >= target_days:
                break

    return chosen


def _reason_selected(
    profile: CandidateProfile,
    curriculum_day: CurriculumDay,
    mission: MissionSignal | None,
    selected_modules: set[int],
) -> str:
    breadth_note = (
        " It adds module breadth to the interview."
        if curriculum_day.module_number not in selected_modules
        else ""
    )
    preferred = curriculum_day.module_number in _preferred_modules(profile.job_role)
    role_note = (
        f" It is relevant to the candidate's {profile.job_role} background."
        if preferred
        else ""
    )

    if mission is None:
        return (
            "Selected as an early-curriculum exploratory area because too few mission "
            "states were available." + breadth_note
        )
    if mission.state is MissionState.FAILED:
        return (
            f"Selected as a diagnostic gap check after {mission.attempts} unsuccessful attempts."
            + breadth_note
            + role_note
        )
    if mission.state is MissionState.SKIPPED:
        return (
            "Selected only as a gap check; the candidate did not complete this mission."
            + breadth_note
            + role_note
        )
    if mission.attempts == 1:
        return (
            "Selected as a demonstrated first-try strength for deeper verification."
            + breadth_note
            + role_note
        )
    if mission.attempts >= 3:
        return (
            f"Selected because the candidate passed after {mission.attempts} attempts, "
            "making it useful for a deeper probe."
            + breadth_note
            + role_note
        )
    return (
        f"Selected as demonstrated completed material after {mission.attempts} attempts."
        + breadth_note
        + role_note
    )


def build_interview_plan(
    profile: CandidateProfile,
    catalog: CurriculumCatalog,
    *,
    minimum_days: int = MINIMUM_DAYS,
    minimum_questions: int = MINIMUM_QUESTIONS,
) -> InterviewPlan:
    """Build a deterministic curriculum-grounded plan for a future adaptive interviewer."""
    target_days = max(minimum_days, MINIMUM_DAYS)
    required_questions = max(minimum_questions, MINIMUM_QUESTIONS)
    passed_selection = _select_passed_days(profile, catalog, target_days)
    selected_entries = _fallback_selections(profile, catalog, passed_selection, target_days)

    if len(selected_entries) < target_days:
        raise ValueError("unable to construct the required curriculum-day coverage")

    selected_modules: set[int] = set()
    planned_areas: list[PlannedArea] = []
    for day_number, mission in selected_entries[:target_days]:
        curriculum_day = catalog.day(day_number)
        reason = _reason_selected(profile, curriculum_day, mission, selected_modules)
        selected_modules.add(curriculum_day.module_number)
        evidence = [f"Demonstrates: {objective}" for objective in curriculum_day.objectives[:3]]
        planned_areas.append(
            PlannedArea(
                day=curriculum_day.day,
                module=curriculum_day.module,
                topic=curriculum_day.title,
                intent=_intent(mission),
                difficulty=_difficulty(profile, mission),
                objectives=curriculum_day.objectives,
                tools=curriculum_day.tools,
                interaction_types=interactions_for_day(curriculum_day.day),
                evidence_to_look_for=evidence,
                reason_selected=reason,
                question_budget=QUESTIONS_PER_AREA,
            )
        )

    planned_questions = max(
        required_questions,
        sum(area.question_budget for area in planned_areas),
    )
    if planned_questions > sum(area.question_budget for area in planned_areas):
        planned_areas[0].question_budget += planned_questions - sum(
            area.question_budget for area in planned_areas
        )

    return InterviewPlan(
        candidate_id=profile.candidate_id,
        profile=PlannerProfileSummary(
            experience_level=profile.experience_level,
            strong_days=profile.strong_days,
            weaker_days=profile.weaker_days,
            failed_days=profile.failed_days,
            skipped_days=profile.skipped_days,
            first_try_rate=profile.first_try_rate,
            commit_days=profile.commit_days,
        ),
        plan=planned_areas,
        minimum_questions=required_questions,
        minimum_days=target_days,
        planned_questions=sum(area.question_budget for area in planned_areas),
    )
