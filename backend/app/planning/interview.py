from __future__ import annotations

from app.curriculum.models import CurriculumCatalog
from app.planning.interactions import interactions_for_day
from app.planning.models import (
    MINIMUM_DAYS,
    MINIMUM_QUESTIONS,
    QUESTIONS_PER_AREA,
    Difficulty,
    InterviewPlan,
    PlanIntent,
    PlannedArea,
    PlannerProfileSummary,
)
from app.planning.rules import difficulty_for, intent_for, preferred_modules, reason_selected
from app.profiling.candidate import CandidateProfile, MissionSignal, MissionState

__all__ = ["Difficulty", "InterviewPlan", "PlanIntent", "build_interview_plan"]


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
    preferred: tuple[int, ...],
) -> MissionSignal | None:
    if not candidates:
        return None
    selected_modules = {catalog.day(signal.day).module_number for signal in selected}
    preferred_set = set(preferred)
    return min(
        candidates,
        key=lambda signal: (
            catalog.day(signal.day).module_number in selected_modules,
            catalog.day(signal.day).module_number not in preferred_set,
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

    preferred = preferred_modules(profile.job_role)
    selected: list[MissionSignal] = []

    weak = [signal for signal in passed if signal.attempts >= 3]
    weak_pick = _pick_best(weak, catalog, selected, preferred)
    if weak_pick is not None:
        selected.append(weak_pick)

    strong = [signal for signal in passed if signal.attempts == 1 and signal not in selected]
    strong_pick = _pick_best(strong, catalog, selected, preferred)
    if strong_pick is not None and len(selected) < target_days:
        selected.append(strong_pick)

    role_relevant = [
        signal
        for signal in passed
        if signal not in selected and catalog.day(signal.day).module_number in preferred
    ]
    role_pick = _pick_best(role_relevant, catalog, selected, preferred)
    if role_pick is not None and len(selected) < target_days:
        selected.append(role_pick)

    while len(selected) < target_days:
        remaining = [signal for signal in passed if signal not in selected]
        pick = _pick_best(remaining, catalog, selected, preferred)
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
    preferred = preferred_modules(profile.job_role)

    for state in (MissionState.FAILED, MissionState.SKIPPED):
        while len(chosen) < target_days:
            state_candidates = [
                signal
                for signal in profile.mission_signals
                if signal.state is state and signal.day not in chosen_days
            ]
            picked_signals = [signal for _, signal in chosen if signal is not None]
            pick = _pick_best(state_candidates, catalog, picked_signals, preferred)
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
        reason = reason_selected(profile, curriculum_day, mission, selected_modules)
        selected_modules.add(curriculum_day.module_number)
        evidence = [f"Demonstrates: {objective}" for objective in curriculum_day.objectives[:3]]
        planned_areas.append(
            PlannedArea(
                day=curriculum_day.day,
                module=curriculum_day.module,
                topic=curriculum_day.title,
                activity_type=curriculum_day.activity_type,
                intent=intent_for(mission),
                difficulty=difficulty_for(profile, mission),
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
