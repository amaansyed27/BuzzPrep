from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMError(Exception):
    """Base class for sanitized provider-neutral LLM failures."""


class LLMConfigurationError(LLMError):
    pass


class LLMProviderError(LLMError):
    pass


class LLMProviderRequestError(LLMProviderError):
    """Non-retryable provider request/configuration failure.

    Fallback routing intentionally does not catch this error. A rejected schema,
    malformed provider request, or invalid credential must be fixed rather than
    hidden by another provider.
    """


class LLMStructuredOutputError(LLMError):
    pass


class LLMProvider(Protocol):
    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> ModelT: ...
