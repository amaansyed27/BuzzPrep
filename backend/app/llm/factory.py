from __future__ import annotations

import os

from app.llm.base import LLMConfigurationError, LLMProvider
from app.llm.fake import FakeLLMProvider
from app.llm.fallback import FallbackLLMProvider
from app.llm.gemini import GeminiLLMProvider
from app.llm.openai_compatible import GroqLLMProvider, OpenRouterLLMProvider


def _build_single_provider(
    name: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> LLMProvider:
    normalized = name.strip().lower()
    if normalized == "fake":
        return FakeLLMProvider()
    if normalized in {"gemini", "google"}:
        return GeminiLLMProvider(
            api_key=api_key if api_key is not None else os.getenv("LLM_API_KEY"),
            model=model if model is not None else os.getenv("LLM_MODEL"),
        )
    if normalized == "groq":
        return GroqLLMProvider(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )
    if normalized == "openrouter":
        return OpenRouterLLMProvider(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        )
    raise LLMConfigurationError(f"Unsupported LLM provider '{name}'")


def build_llm_provider(
    *,
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    provider_chain: str | None = None,
) -> LLMProvider:
    """Build the configured provider without coupling interview graph code to a vendor."""
    chain_value = provider_chain if provider_chain is not None else os.getenv("LLM_PROVIDER_CHAIN", "")
    chain_names = [part.strip() for part in chain_value.split(",") if part.strip()]
    if chain_names:
        providers = [_build_single_provider(name) for name in chain_names]
        return providers[0] if len(providers) == 1 else FallbackLLMProvider(providers)

    name = (provider_name if provider_name is not None else os.getenv("LLM_PROVIDER", "")).strip()
    if not name:
        raise LLMConfigurationError(
            "LLM_PROVIDER is required; use 'gemini' for normal runs or explicitly set 'fake'"
        )
    return _build_single_provider(name, api_key=api_key, model=model)
