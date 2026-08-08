from __future__ import annotations

from enum import StrEnum


class InteractionType(StrEnum):
    SYSTEM_CANVAS = "system_canvas"
    CONFIGURATION_LAB = "configuration_lab"
    DATA_WORKBENCH = "data_workbench"
    PROMPT_SCHEMA_EDITOR = "prompt_schema_editor"
    CODE_CONFIG_REPAIR = "code_config_repair"
    LOGS_METRICS_EXPLORER = "logs_metrics_explorer"
    TEST_EVALUATION_RUNNER = "test_evaluation_runner"
    INCIDENT_SIMULATOR = "incident_simulator"
    ARCHITECTURE_CRITIQUE = "architecture_critique"


_INTERACTIONS_BY_DAY: dict[int, tuple[InteractionType, ...]] = {
    1: (InteractionType.CODE_CONFIG_REPAIR, InteractionType.CONFIGURATION_LAB),
    2: (InteractionType.CONFIGURATION_LAB, InteractionType.CODE_CONFIG_REPAIR),
    3: (InteractionType.SYSTEM_CANVAS, InteractionType.CODE_CONFIG_REPAIR),
    4: (InteractionType.DATA_WORKBENCH, InteractionType.CODE_CONFIG_REPAIR),
    5: (InteractionType.DATA_WORKBENCH, InteractionType.CODE_CONFIG_REPAIR),
    6: (InteractionType.DATA_WORKBENCH, InteractionType.SYSTEM_CANVAS),
    7: (InteractionType.TEST_EVALUATION_RUNNER, InteractionType.DATA_WORKBENCH),
    8: (InteractionType.CONFIGURATION_LAB, InteractionType.ARCHITECTURE_CRITIQUE),
    9: (InteractionType.DATA_WORKBENCH, InteractionType.TEST_EVALUATION_RUNNER),
    10: (InteractionType.SYSTEM_CANVAS, InteractionType.CODE_CONFIG_REPAIR),
    11: (InteractionType.SYSTEM_CANVAS, InteractionType.PROMPT_SCHEMA_EDITOR),
    12: (InteractionType.PROMPT_SCHEMA_EDITOR, InteractionType.TEST_EVALUATION_RUNNER),
    13: (InteractionType.PROMPT_SCHEMA_EDITOR, InteractionType.CODE_CONFIG_REPAIR),
    14: (InteractionType.ARCHITECTURE_CRITIQUE, InteractionType.DATA_WORKBENCH),
    15: (InteractionType.CONFIGURATION_LAB, InteractionType.TEST_EVALUATION_RUNNER),
    16: (InteractionType.CODE_CONFIG_REPAIR, InteractionType.SYSTEM_CANVAS),
    17: (InteractionType.CODE_CONFIG_REPAIR, InteractionType.SYSTEM_CANVAS),
    18: (InteractionType.CODE_CONFIG_REPAIR, InteractionType.LOGS_METRICS_EXPLORER),
    19: (InteractionType.PROMPT_SCHEMA_EDITOR, InteractionType.DATA_WORKBENCH),
    20: (InteractionType.SYSTEM_CANVAS, InteractionType.CODE_CONFIG_REPAIR),
    21: (InteractionType.SYSTEM_CANVAS, InteractionType.LOGS_METRICS_EXPLORER),
    22: (InteractionType.SYSTEM_CANVAS, InteractionType.ARCHITECTURE_CRITIQUE),
    23: (InteractionType.SYSTEM_CANVAS, InteractionType.CODE_CONFIG_REPAIR),
    24: (InteractionType.SYSTEM_CANVAS, InteractionType.INCIDENT_SIMULATOR),
    25: (InteractionType.TEST_EVALUATION_RUNNER, InteractionType.ARCHITECTURE_CRITIQUE),
    26: (InteractionType.TEST_EVALUATION_RUNNER, InteractionType.LOGS_METRICS_EXPLORER),
    27: (InteractionType.INCIDENT_SIMULATOR, InteractionType.CODE_CONFIG_REPAIR),
    28: (InteractionType.CONFIGURATION_LAB, InteractionType.INCIDENT_SIMULATOR),
    29: (InteractionType.LOGS_METRICS_EXPLORER, InteractionType.INCIDENT_SIMULATOR),
    30: (InteractionType.TEST_EVALUATION_RUNNER, InteractionType.INCIDENT_SIMULATOR),
    31: (InteractionType.ARCHITECTURE_CRITIQUE, InteractionType.SYSTEM_CANVAS),
}


def interactions_for_day(day: int) -> list[InteractionType]:
    try:
        return list(_INTERACTIONS_BY_DAY[day])
    except KeyError as exc:
        raise ValueError(f"No interaction mapping exists for curriculum day {day}") from exc
