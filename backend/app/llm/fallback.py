from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any

from app.llm.base import (
    LLMProvider,
    LLMProviderError,
    LLMProviderRequestError,
    LLMStructuredOutputError,
    ModelT,
)

logger = logging.getLogger(__name__)


class FallbackLLMProvider:
    """Try provider availability fallbacks without masking rejected requests."""

    provider_name = "fallback"

    def __init__(self, providers: Sequence[LLMProvider]) -> None:
        if not providers:
            raise ValueError("FallbackLLMProvider requires at least one provider")
        self.providers = list(providers)

    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> ModelT:
        failures: list[Exception] = []
        for index, provider in enumerate(self.providers):
            name = getattr(provider, "provider_name", provider.__class__.__name__)
            try:
                result = provider.generate_structured(
                    task=task,
                    system_prompt=system_prompt,
                    context=context,
                    output_schema=output_schema,
                )
                logger.info(
                    "Structured generation served provider=%s task=%s fallback_index=%s",
                    name,
                    task,
                    index,
                )
                return result
            except LLMProviderRequestError:
                raise
            except (LLMProviderError, LLMStructuredOutputError) as exc:
                failures.append(exc)
                logger.warning(
                    "Structured provider fallback provider=%s task=%s fallback_index=%s error_type=%s",
                    name,
                    task,
                    index,
                    type(exc).__name__,
                )

        raise LLMProviderError("All configured LLM providers are unavailable") from failures[-1]
