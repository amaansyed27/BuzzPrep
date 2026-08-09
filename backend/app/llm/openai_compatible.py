from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import ValidationError

from app.llm.base import (
    LLMConfigurationError,
    LLMProviderError,
    LLMProviderRequestError,
    LLMStructuredOutputError,
    ModelT,
)

logger = logging.getLogger(__name__)

_SENSITIVE_FIELD_FRAGMENTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "secret",
    "token",
)


def normalize_strict_json_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize Pydantic JSON Schema for strict OpenAI-compatible decoding."""

    def normalize(value: Any) -> Any:
        if isinstance(value, Mapping):
            normalized = {
                str(key): normalize(item)
                for key, item in value.items()
                if key not in {"default", "examples"}
            }
            if normalized.get("type") == "object" or "properties" in normalized:
                properties = normalized.get("properties", {})
                if isinstance(properties, Mapping):
                    normalized["required"] = list(properties)
                    normalized["additionalProperties"] = False
            return normalized
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    return normalize(schema)


def _sanitize_provider_body(value: Any, api_key: str) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            if any(fragment in normalized_key for fragment in _SENSITIVE_FIELD_FRAGMENTS):
                sanitized[str(key)] = "<redacted>"
            else:
                sanitized[str(key)] = _sanitize_provider_body(item, api_key)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_provider_body(item, api_key) for item in value]
    if isinstance(value, str) and api_key:
        return value.replace(api_key, "<redacted>")
    return value


class OpenAICompatibleLLMProvider:
    """Structured-output adapter for OpenAI-compatible chat completions APIs."""

    def __init__(
        self,
        *,
        provider_name: str,
        endpoint: str,
        api_key: str | None,
        model: str | None,
        timeout_seconds: float = 30.0,
        max_attempts: int = 2,
        client: httpx.Client | None = None,
        extra_headers: Mapping[str, str] | None = None,
        provider_preferences: Mapping[str, Any] | None = None,
    ) -> None:
        self.provider_name = provider_name
        self.endpoint = endpoint
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max(1, max_attempts)
        self._client = client
        self.extra_headers = dict(extra_headers or {})
        self.provider_preferences = dict(provider_preferences or {})

    def _validate_configuration(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError(
                f"{self.provider_name.upper()}_API_KEY is required for {self.provider_name}"
            )
        if not self.model:
            raise LLMConfigurationError(
                f"{self.provider_name.upper()}_MODEL is required for {self.provider_name}"
            )

    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> ModelT:
        self._validate_configuration()
        schema_name = "".join(character if character.isalnum() else "_" for character in task)
        request_body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Task: {task}\nUse only the supplied structured context. "
                        "Return only the requested structured result.\nContext JSON:\n"
                        + json.dumps(context, ensure_ascii=False, separators=(",", ":"))
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name[:64] or "buzzprep_result",
                    "strict": True,
                    "schema": normalize_strict_json_schema(output_schema.model_json_schema()),
                },
            },
            "temperature": 0.2,
        }
        if self.provider_preferences:
            request_body["provider"] = self.provider_preferences

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                client = self._client
                response = (
                    client.post(
                        self.endpoint,
                        headers=headers,
                        json=request_body,
                        timeout=self.timeout_seconds,
                    )
                    if client is not None
                    else httpx.post(
                        self.endpoint,
                        headers=headers,
                        json=request_body,
                        timeout=self.timeout_seconds,
                    )
                )
                response.raise_for_status()
                try:
                    return self._parse_response(response, output_schema)
                except LLMStructuredOutputError as exc:
                    logger.warning(
                        "%s returned invalid structured output task=%s model=%s attempt=%s/%s",
                        self.provider_name,
                        task,
                        self.model,
                        attempt,
                        self.max_attempts,
                    )
                    last_error = exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                self._log_provider_error(task, attempt, exc.response)
                if status_code == 404 or status_code in {408, 409, 429} or status_code >= 500:
                    last_error = exc
                    continue
                raise LLMProviderRequestError(
                    "The LLM provider rejected the structured generation request"
                ) from exc
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                logger.warning(
                    "%s transient request failure task=%s model=%s attempt=%s/%s error_type=%s",
                    self.provider_name,
                    task,
                    self.model,
                    attempt,
                    self.max_attempts,
                    type(exc).__name__,
                )
                last_error = exc

        if isinstance(last_error, LLMStructuredOutputError):
            raise LLMStructuredOutputError(
                "The LLM provider returned invalid structured output"
            ) from last_error
        raise LLMProviderError("The configured LLM provider is unavailable") from last_error

    def _log_provider_error(self, task: str, attempt: int, response: httpx.Response) -> None:
        try:
            provider_body: Any = response.json()
        except json.JSONDecodeError:
            provider_body = {"message": response.text[:1000]}
        sanitized = _sanitize_provider_body(provider_body, self.api_key)
        serialized = json.dumps(sanitized, ensure_ascii=False, separators=(",", ":"))[:2000]
        category = (
            "transient"
            if response.status_code in {404, 408, 409, 429} or response.status_code >= 500
            else "request"
        )
        logger.warning(
            "%s %s failure task=%s model=%s status=%s attempt=%s/%s provider_body=%s",
            self.provider_name,
            category,
            task,
            self.model,
            response.status_code,
            attempt,
            self.max_attempts,
            serialized,
        )

    @staticmethod
    def _parse_response(response: httpx.Response, output_schema: type[ModelT]) -> ModelT:
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(
                    str(part.get("text", "")) for part in content if isinstance(part, Mapping)
                )
            if not isinstance(content, str):
                raise TypeError("Structured response content must be text")
            return output_schema.model_validate_json(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise LLMStructuredOutputError(
                "The LLM provider returned invalid structured output"
            ) from exc


class GroqLLMProvider(OpenAICompatibleLLMProvider):
    def __init__(self, *, api_key: str | None, model: str | None, **kwargs: Any) -> None:
        super().__init__(
            provider_name="groq",
            endpoint="https://api.groq.com/openai/v1/chat/completions",
            api_key=api_key,
            model=model,
            **kwargs,
        )


class OpenRouterLLMProvider(OpenAICompatibleLLMProvider):
    def __init__(self, *, api_key: str | None, model: str | None, **kwargs: Any) -> None:
        super().__init__(
            provider_name="openrouter",
            endpoint="https://openrouter.ai/api/v1/chat/completions",
            api_key=api_key,
            model=model,
            extra_headers={
                "HTTP-Referer": "https://buzzprep-web.vercel.app",
                "X-Title": "BuzzPrep",
            },
            provider_preferences={"require_parameters": True},
            **kwargs,
        )
