from __future__ import annotations

import logging
import os

from app.memory.base import MemoryService, NoopMemoryService
from app.memory.breeth import BreethMemoryService

logger = logging.getLogger(__name__)


def _enabled(value: str | None) -> bool:
    return (value or "true").strip().lower() not in {"0", "false", "no", "off"}


def build_memory_service(
    *,
    enabled: bool | None = None,
    api_key: str | None = None,
) -> MemoryService:
    use_breeth = _enabled(os.getenv("BREETH_ENABLED")) if enabled is None else enabled
    if not use_breeth:
        return NoopMemoryService()

    resolved_key = (api_key if api_key is not None else os.getenv("BREETH_API_KEY", "")).strip()
    if not resolved_key:
        logger.warning("Breeth is enabled but BREETH_API_KEY is missing; semantic memory is disabled")
        return NoopMemoryService()
    return BreethMemoryService(api_key=resolved_key)
