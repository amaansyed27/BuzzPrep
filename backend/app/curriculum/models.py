from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


class CurriculumModuleSource(BaseModel):
    n: int = Field(ge=1)
    title: str = Field(min_length=1)
    days: tuple[int, int]

    @field_validator("days", mode="before")
    @classmethod
    def validate_day_range_shape(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("module days must contain [start_day, end_day]")
        return value

    @model_validator(mode="after")
    def validate_day_range(self) -> CurriculumModuleSource:
        start_day, end_day = self.days
        if start_day < 1 or end_day > 31 or start_day > end_day:
            raise ValueError("module day range must be within days 1..31")
        return self


class CurriculumDaySource(BaseModel):
    day: int = Field(ge=1, le=31)
    title: str = Field(min_length=1)
    type: str = Field(min_length=1)
    tools: list[str] = Field(default_factory=list)
    objectives: list[str] = Field(min_length=1)


class CurriculumDocument(BaseModel):
    cohort: str = Field(min_length=1)
    modules: list[CurriculumModuleSource] = Field(min_length=1)
    days: list[CurriculumDaySource] = Field(min_length=1)


class CurriculumModule(BaseModel):
    number: int = Field(ge=1)
    title: str = Field(min_length=1)
    start_day: int = Field(ge=1, le=31)
    end_day: int = Field(ge=1, le=31)


class CurriculumDay(BaseModel):
    day: int = Field(ge=1, le=31)
    module_number: int = Field(ge=1)
    module: str = Field(min_length=1)
    title: str = Field(min_length=1)
    activity_type: str = Field(min_length=1)
    tools: list[str] = Field(default_factory=list)
    objectives: list[str] = Field(min_length=1)


class CurriculumCatalog(BaseModel):
    cohort: str = Field(min_length=1)
    modules: list[CurriculumModule] = Field(min_length=1)
    days: list[CurriculumDay] = Field(min_length=1)

    def day(self, day_number: int) -> CurriculumDay:
        for curriculum_day in self.days:
            if curriculum_day.day == day_number:
                return curriculum_day
        raise KeyError(f"Curriculum day {day_number} does not exist")
