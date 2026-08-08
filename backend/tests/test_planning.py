from __future__ import annotations

from pathlib import Path

import pytest

from app.curriculum.loader import load_curriculum
from app.planning.interactions import InteractionType
from app.planning.interview import Difficulty, PlanIntent, build_interview_plan
from app.profiling.candidate import MissionState, profile_candidate
from app.profiling.loader import load_candidates


def _profiles():
    return [profile_candidate(candidate) for candidate in load_candidates()]


def _profile(candidate_id: str):
    return next(profile for profile in _profiles() if profile.candidate_id == candidate_id)


def test_curriculum_loader_loads_all_31_days() -> None:
    catalog = load_curriculum()

    assert [day.day for day in catalog.days] == list(range(1, 32))
    assert len(catalog.modules) == 8
    assert catalog.day(31).title == "Capstone Project & Final Demo"


def test_candidate_loader_and_profiler_handle_all_supplied_candidates() -> None:
    candidates = load_candidates()
    profiles = [profile_candidate(candidate) for candidate in candidates]

    assert len(candidates) == 20
    assert len({profile.candidate_id for profile in profiles}) == 20
    assert all(profile.name and profile.job_role for profile in profiles)
    assert all(
        profile.total_completed_missions >= profile.observed_passed_missions
        for profile in profiles
    )


def test_passed_failed_and_skipped_missions_remain_distinct() -> None:
    gerald = _profile("CAND-010")

    assert 7 in gerald.passed_days
    assert {8, 10, 22}.issubset(gerald.failed_days)
    assert {27, 28}.issubset(gerald.skipped_days)
    assert not (set(gerald.passed_days) & set(gerald.failed_days))
    assert not (set(gerald.passed_days) & set(gerald.skipped_days))


def test_every_supplied_candidate_gets_required_day_and_question_coverage() -> None:
    catalog = load_curriculum()

    for profile in _profiles():
        plan = build_interview_plan(profile, catalog)
        assert plan.minimum_days >= 4
        assert plan.minimum_questions >= 8
        assert len({area.day for area in plan.plan}) >= 4
        assert plan.planned_questions >= 8
        assert sum(area.question_budget for area in plan.plan) >= 8


def test_sparse_candidate_uses_four_demonstrated_passed_days() -> None:
    catalog = load_curriculum()
    profile = _profile("CAND-016")
    plan = build_interview_plan(profile, catalog)

    assert profile.passed_days == [1, 8, 16, 31]
    assert {area.day for area in plan.plan} == {1, 8, 16, 31}
    assert all(area.intent is PlanIntent.ASSESSMENT for area in plan.plan)
    assert not ({7, 12, 22} & {area.day for area in plan.plan})


def test_strong_candidate_gets_advanced_and_broad_plan() -> None:
    catalog = load_curriculum()
    profile = _profile("CAND-018")
    plan = build_interview_plan(profile, catalog)

    modules = {catalog.day(area.day).module_number for area in plan.plan}
    assert profile.first_try_rate == 1.0
    assert any(area.difficulty is Difficulty.ADVANCED for area in plan.plan)
    assert len(modules) == 4


def test_weak_multiple_attempt_candidate_gets_introductory_probes() -> None:
    catalog = load_curriculum()
    profile = _profile("CAND-017")
    plan = build_interview_plan(profile, catalog)

    assert profile.weaker_days
    assert all(area.day in profile.passed_days for area in plan.plan)
    assert any(area.difficulty is Difficulty.INTRODUCTORY for area in plan.plan)
    assert any(profile.attempts_by_day[area.day] >= 4 for area in plan.plan)


def test_skipped_topics_are_never_profiled_as_completed() -> None:
    profile = _profile("CAND-014")

    assert 8 in profile.skipped_days
    assert 8 not in profile.passed_days
    signal = profile.mission(8)
    assert signal is not None
    assert signal.state is MissionState.SKIPPED
    assert not signal.first_try


def test_failed_topics_are_never_profiled_as_passed() -> None:
    profile = _profile("CAND-010")

    for day in (8, 10, 22):
        signal = profile.mission(day)
        assert signal is not None
        assert signal.state is MissionState.FAILED
        assert day not in profile.passed_days
        assert day not in profile.strong_days


def test_selected_days_are_grounded_in_curriculum() -> None:
    catalog = load_curriculum()
    valid_days = {day.day for day in catalog.days}

    for profile in _profiles():
        plan = build_interview_plan(profile, catalog)
        assert {area.day for area in plan.plan}.issubset(valid_days)
        for area in plan.plan:
            source_day = catalog.day(area.day)
            assert area.topic == source_day.title
            assert area.activity_type == source_day.activity_type
            assert area.objectives == source_day.objectives
            assert area.tools == source_day.tools


def test_interaction_types_are_valid_for_every_plan() -> None:
    catalog = load_curriculum()
    valid_values = {interaction.value for interaction in InteractionType}

    for profile in _profiles():
        plan = build_interview_plan(profile, catalog)
        for area in plan.plan:
            assert area.interaction_types
            assert all(interaction.value in valid_values for interaction in area.interaction_types)


def test_difficulty_values_are_valid_for_every_plan() -> None:
    catalog = load_curriculum()
    valid_values = {difficulty.value for difficulty in Difficulty}

    for profile in _profiles():
        plan = build_interview_plan(profile, catalog)
        assert all(area.difficulty.value in valid_values for area in plan.plan)


def test_plan_is_deterministic_for_identical_input() -> None:
    catalog = load_curriculum()
    profile = _profile("CAND-001")

    first = build_interview_plan(profile, catalog)
    second = build_interview_plan(profile, catalog)

    assert first.model_dump(mode="json", by_alias=True) == second.model_dump(
        mode="json", by_alias=True
    )


def test_resource_loading_does_not_depend_on_current_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert len(load_curriculum().days) == 31
    assert len(load_candidates()) == 20


def test_failed_and_skipped_topics_are_explicit_when_needed_as_fallback() -> None:
    catalog = load_curriculum()
    candidate = {
        "member": {
            "id": "CUSTOM-SPARSE",
            "name": "Sparse Candidate",
            "jobRole": "Junior Developer",
            "yearsExperience": 0,
            "education": "Bootcamp",
            "status": "IN_PROGRESS",
        },
        "missions": [
            {"day": 1, "title": catalog.day(1).title, "passed": True, "attempts": 1},
            {"day": 3, "title": catalog.day(3).title, "passed": True, "attempts": 2},
            {"day": 7, "title": catalog.day(7).title, "passed": False, "attempts": 3},
            {"day": 8, "title": catalog.day(8).title, "skipped": True},
        ],
        "signals": {"commitDays": 3, "missionsCompleted": 3, "missionsFirstTry": 1},
    }

    plan = build_interview_plan(profile_candidate(candidate), catalog)
    by_day = {area.day: area for area in plan.plan}

    assert by_day[7].intent is PlanIntent.DIAGNOSTIC
    assert by_day[8].intent is PlanIntent.GAP_CHECK
    assert by_day[7].difficulty is Difficulty.INTRODUCTORY
    assert by_day[8].difficulty is Difficulty.INTRODUCTORY
