from __future__ import annotations

from app.curriculum.models import CurriculumDay
from app.planning.models import Difficulty, PlanIntent
from app.profiling.candidate import (
    CandidateProfile,
    ExperienceLevel,
    MissionSignal,
    MissionState,
)

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


def preferred_modules(job_role: str) -> tuple[int, ...]:
    normalized = job_role.lower()
    for terms, modules in _ROLE_MODULE_RULES:
        if any(term in normalized for term in terms):
            return modules
    return ()


def difficulty_for(profile: CandidateProfile, mission: MissionSignal | None) -> Difficulty:
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


def intent_for(mission: MissionSignal | None) -> PlanIntent:
    if mission is None:
        return PlanIntent.EXPLORATORY
    if mission.state is MissionState.PASSED:
        return PlanIntent.ASSESSMENT
    if mission.state is MissionState.FAILED:
        return PlanIntent.DIAGNOSTIC
    return PlanIntent.GAP_CHECK


def reason_selected(
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
    preferred = curriculum_day.module_number in preferred_modules(profile.job_role)
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
