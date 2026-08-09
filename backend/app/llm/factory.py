from __future__ import annotations

import os

from app.llm.base import LLMConfigurationError, LLMProvider
from app.llm.fake import FakeLLMProvider
from app.llm.gemini import GeminiLLMProvider


def build_llm_provider(
    *,
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> LLMProvider:
    """Build the configured provider without coupling interview graph code to a vendor."""
    name = (provider_name if provider_name is not None else os.getenv("LLM_PROVIDER", "")).strip()
    normalized = name.lower()

    if not normalized:
        raise LLMConfigurationError(
            "LLM_PROVIDER is required; use 'gemini' for normal runs or explicitly set 'fake'"
        )

    if normalized == "fake":
        return FakeLLMProvider()
    if normalized in {"gemini", "google"}:
        return GeminiLLMProvider(
            api_key=api_key if api_key is not None else os.getenv("LLM_API_KEY"),
            model=model if model is not None else os.getenv("LLM_MODEL"),
        )
    raise LLMConfigurationError(f"Unsupported LLM provider '{name}'")
