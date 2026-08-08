from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MissionState(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExperienceLevel(StrEnum):
    INTRODUCTORY = "introductory"
    STANDARD = "standard"
    ADVANCED = "advanced"


class CandidateMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    candidate_id: str = Field(alias="id", min_length=1)
    name: str = Field(min_length=1)
    job_role: str = Field(alias="jobRole", min_length=1)
    years_experience: int = Field(alias="yearsExperience", ge=0)
    education: str | None = None
    status: str = Field(min_length=1)


class CandidateMission(BaseModel):
    day: int = Field(ge=1, le=31)
    title: str = Field(min_length=1)
    passed: bool | None = None
    skipped: bool = False
    attempts: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_state(self) -> CandidateMission:
        if self.skipped and self.passed is True:
            raise ValueError("a mission cannot be both passed and skipped")
        if not self.skipped and self.passed is None:
            raise ValueError("a non-skipped mission must declare passed true or false")
        if not self.skipped and self.attempts < 1:
            raise ValueError("a passed or failed mission must have at least one attempt")
        return self

    @property
    def state(self) -> MissionState:
        if self.skipped:
            return MissionState.SKIPPED
        if self.passed is True:
            return MissionState.PASSED
        return MissionState.FAILED


class CandidateSignals(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    commit_days: int = Field(alias="commitDays", ge=0)
    missions_completed: int = Field(alias="missionsCompleted", ge=0)
    missions_first_try: int = Field(alias="missionsFirstTry", ge=0)


class CandidateRecord(BaseModel):
    member: CandidateMember
    missions: list[CandidateMission] = Field(default_factory=list)
    signals: CandidateSignals


class MissionSignal(BaseModel):
    day: int = Field(ge=1, le=31)
    title: str
    state: MissionState
    attempts: int = Field(ge=0)
    first_try: bool


class CandidateProfile(BaseModel):
    candidate_id: str
    name: str
    job_role: str
    years_experience: int
    education: str | None
    cohort_status: str
    experience_level: ExperienceLevel
    technical_role: bool
    mission_signals: list[MissionSignal]
    passed_days: list[int]
    failed_days: list[int]
    skipped_days: list[int]
    strong_days: list[int]
    weaker_days: list[int]
    attempts_by_day: dict[int, int]
    first_try_passed_days: list[int]
    observed_passed_missions: int
    total_completed_missions: int
    commit_days: int
    missions_first_try: int
    first_try_rate: float = Field(ge=0.0, le=1.0)

    def mission(self, day: int) -> MissionSignal | None:
        for signal in self.mission_signals:
            if signal.day == day:
                return signal
        return None


_TECHNICAL_ROLE_TERMS = (
    "engineer",
    "developer",
    "architect",
    "computer science",
    "devops",
    "data",
    "ai ",
    "ml ",
    "it support",
)


def _is_technical_role(job_role: str) -> bool:
    normalized = f"{job_role.lower()} "
    return any(term in normalized for term in _TECHNICAL_ROLE_TERMS)


def _experience_level(record: CandidateRecord, first_try_rate: float) -> ExperienceLevel:
    technical_role = _is_technical_role(record.member.job_role)
    if first_try_rate < 0.25:
        return ExperienceLevel.INTRODUCTORY
    if technical_role and (
        first_try_rate >= 0.8
        or (record.member.years_experience >= 8 and first_try_rate >= 0.5)
    ):
        return ExperienceLevel.ADVANCED
    return ExperienceLevel.STANDARD


def profile_candidate(candidate: CandidateRecord | dict[str, object]) -> CandidateProfile:
    """Interpret deterministic interview signals without treating status as mission success."""
    record = (
        candidate
        if isinstance(candidate, CandidateRecord)
        else CandidateRecord.model_validate(candidate)
    )

    mission_signals = [
        MissionSignal(
            day=mission.day,
            title=mission.title,
            state=mission.state,
            attempts=mission.attempts,
            first_try=mission.state is MissionState.PASSED and mission.attempts == 1,
        )
        for mission in sorted(record.missions, key=lambda item: item.day)
    ]

    passed_days = [signal.day for signal in mission_signals if signal.state is MissionState.PASSED]
    failed_days = [signal.day for signal in mission_signals if signal.state is MissionState.FAILED]
    skipped_days = [
        signal.day for signal in mission_signals if signal.state is MissionState.SKIPPED
    ]
    first_try_passed_days = [
        signal.day
        for signal in mission_signals
        if signal.state is MissionState.PASSED and signal.first_try
    ]
    weaker_days = [
        signal.day
        for signal in mission_signals
        if signal.state is MissionState.PASSED and signal.attempts >= 3
    ]
    first_try_rate = (
        record.signals.missions_first_try / record.signals.missions_completed
        if record.signals.missions_completed
        else 0.0
    )

    return CandidateProfile(
        candidate_id=record.member.candidate_id,
        name=record.member.name,
        job_role=record.member.job_role,
        years_experience=record.member.years_experience,
        education=record.member.education,
        cohort_status=record.member.status,
        experience_level=_experience_level(record, first_try_rate),
        technical_role=_is_technical_role(record.member.job_role),
        mission_signals=mission_signals,
        passed_days=passed_days,
        failed_days=failed_days,
        skipped_days=skipped_days,
        strong_days=first_try_passed_days,
        weaker_days=weaker_days,
        attempts_by_day={signal.day: signal.attempts for signal in mission_signals},
        first_try_passed_days=first_try_passed_days,
        observed_passed_missions=len(passed_days),
        total_completed_missions=record.signals.missions_completed,
        commit_days=record.signals.commit_days,
        missions_first_try=record.signals.missions_first_try,
        first_try_rate=round(first_try_rate, 4),
    )
