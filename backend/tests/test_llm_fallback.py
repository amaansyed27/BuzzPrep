from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from app.llm.base import (
    LLMProviderError,
    LLMProviderRequestError,
    LLMStructuredOutputError,
)
from app.llm.fallback import FallbackLLMProvider
from app.llm.openai_compatible import (
    GroqLLMProvider,
    OpenRouterLLMProvider,
    normalize_strict_json_schema,
)


class StructuredResult(BaseModel):
    answer: str
    evidence: str | None = None


class StubProvider:
    def __init__(self, name: str, result: StructuredResult | Exception) -> None:
        self.provider_name = name
        self.result = result
        self.calls = 0

    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[BaseModel],
    ) -> BaseModel:
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        return output_schema.model_validate(self.result.model_dump())


def generate(provider: FallbackLLMProvider) -> StructuredResult:
    return provider.generate_structured(
        task="test",
        system_prompt="Return evidence.",
        context={"candidate": "Sarah"},
        output_schema=StructuredResult,
    )


def test_gemini_success_does_not_call_fallback() -> None:
    gemini = StubProvider("gemini", StructuredResult(answer="primary"))
    groq = StubProvider("groq", StructuredResult(answer="fallback"))

    result = generate(FallbackLLMProvider([gemini, groq]))

    assert result.answer == "primary"
    assert gemini.calls == 1
    assert groq.calls == 0


def test_gemini_transient_failure_falls_back_to_groq() -> None:
    gemini = StubProvider("gemini", LLMProviderError("unavailable"))
    groq = StubProvider("groq", StructuredResult(answer="groq"))

    result = generate(FallbackLLMProvider([gemini, groq]))

    assert result.answer == "groq"
    assert gemini.calls == groq.calls == 1


def test_gemini_and_groq_failure_falls_back_to_openrouter() -> None:
    gemini = StubProvider("gemini", LLMProviderError("unavailable"))
    groq = StubProvider("groq", LLMStructuredOutputError("invalid"))
    openrouter = StubProvider("openrouter", StructuredResult(answer="router", evidence="valid"))

    result = generate(FallbackLLMProvider([gemini, groq, openrouter]))

    assert result == StructuredResult(answer="router", evidence="valid")
    assert gemini.calls == groq.calls == openrouter.calls == 1


def test_all_provider_failures_return_controlled_error() -> None:
    providers = [
        StubProvider("gemini", LLMProviderError("first")),
        StubProvider("groq", LLMStructuredOutputError("second")),
        StubProvider("openrouter", LLMProviderError("third")),
    ]

    with pytest.raises(LLMProviderError, match="All configured LLM providers"):
        generate(FallbackLLMProvider(providers))


def test_rejected_provider_request_never_falls_back() -> None:
    gemini = StubProvider("gemini", LLMProviderRequestError("bad schema"))
    groq = StubProvider("groq", StructuredResult(answer="must not run"))

    with pytest.raises(LLMProviderRequestError, match="bad schema"):
        generate(FallbackLLMProvider([gemini, groq]))

    assert groq.calls == 0


def test_strict_schema_requires_every_property_and_disallows_extras() -> None:
    schema = normalize_strict_json_schema(StructuredResult.model_json_schema())

    assert schema["required"] == ["answer", "evidence"]
    assert schema["additionalProperties"] is False
    assert "default" not in json.dumps(schema)


@pytest.mark.parametrize(
    ("provider_class", "expected_host", "expects_provider_preferences"),
    [
        (GroqLLMProvider, "api.groq.com", False),
        (OpenRouterLLMProvider, "openrouter.ai", True),
    ],
)
def test_openai_compatible_adapters_send_strict_schema_and_validate(
    provider_class: type[GroqLLMProvider | OpenRouterLLMProvider],
    expected_host: str,
    expects_provider_preferences: bool,
) -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["host"] = request.url.host
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            request=request,
            json={
                "choices": [
                    {"message": {"content": '{"answer":"validated","evidence":null}'}}
                ]
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = provider_class(api_key="test-key", model="test-model", client=client)
        result = provider.generate_structured(
            task="structured_task",
            system_prompt="system",
            context={"input": True},
            output_schema=StructuredResult,
        )

    assert result == StructuredResult(answer="validated")
    assert captured["host"] == expected_host
    response_format = captured["body"]["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert response_format["json_schema"]["schema"]["additionalProperties"] is False
    assert ("provider" in captured["body"]) is expects_provider_preferences


def test_openai_compatible_adapter_does_not_retry_schema_400() -> None:
    requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return httpx.Response(
            400,
            request=request,
            json={"error": {"message": "invalid schema"}},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        provider = GroqLLMProvider(
            api_key="test-key",
            model="openai/gpt-oss-120b",
            client=client,
            max_attempts=2,
        )
        with pytest.raises(LLMProviderRequestError):
            provider.generate_structured(
                task="structured_task",
                system_prompt="system",
                context={},
                output_schema=StructuredResult,
            )

    assert requests == 1
