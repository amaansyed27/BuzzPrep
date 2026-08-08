from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.curriculum.models import (
    CurriculumCatalog,
    CurriculumDay,
    CurriculumDocument,
    CurriculumModule,
)

RESOURCE_ROOT = Path(__file__).resolve().parents[3] / "hackathon-resources"
DEFAULT_CURRICULUM_PATH = RESOURCE_ROOT / "curriculum.json"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def load_curriculum(path: str | Path | None = None) -> CurriculumCatalog:
    """Load and validate the supplied 31-day curriculum from a robust resource path."""
    source_path = Path(path) if path is not None else DEFAULT_CURRICULUM_PATH
    document = CurriculumDocument.model_validate(_read_json(source_path))

    day_numbers = [day.day for day in document.days]
    expected_days = set(range(1, 32))
    if len(day_numbers) != 31 or set(day_numbers) != expected_days:
        raise ValueError("curriculum must contain each day from 1 through 31 exactly once")

    module_for_day: dict[int, tuple[int, str]] = {}
    modules: list[CurriculumModule] = []
    for source_module in document.modules:
        start_day, end_day = source_module.days
        module = CurriculumModule(
            number=source_module.n,
            title=source_module.title,
            start_day=start_day,
            end_day=end_day,
        )
        modules.append(module)
        for day_number in range(start_day, end_day + 1):
            if day_number in module_for_day:
                raise ValueError(f"curriculum day {day_number} belongs to multiple modules")
            module_for_day[day_number] = (module.number, module.title)

    if set(module_for_day) != expected_days:
        raise ValueError("curriculum modules must cover every day from 1 through 31")

    normalized_days = []
    for source_day in sorted(document.days, key=lambda item: item.day):
        module_number, module_title = module_for_day[source_day.day]
        normalized_days.append(
            CurriculumDay(
                day=source_day.day,
                module_number=module_number,
                module=module_title,
                title=source_day.title,
                activity_type=source_day.type,
                tools=source_day.tools,
                objectives=source_day.objectives,
            )
        )

    return CurriculumCatalog(
        cohort=document.cohort,
        modules=sorted(modules, key=lambda item: item.number),
        days=normalized_days,
    )
