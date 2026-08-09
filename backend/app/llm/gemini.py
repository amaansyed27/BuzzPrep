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
    LLMStructuredOutputError,
    ModelT,
)

logger = logging.getLogger(__name__)

_SUPPORTED_SCHEMA_KEYS = {
    "$id",
    "$defs",
    "$ref",
    "$anchor",
    "type",
    "format",
    "title",
    "description",
    "enum",
    "items",
    "prefixItems",
    "minItems",
    "maxItems",
    "minimum",
    "maximum",
    "anyOf",
    "oneOf",
    "properties",
    "additionalProperties",
    "required",
    "propertyOrdering",
}
_SENSITIVE_FIELD_FRAGMENTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "secret",
    "token",
)


def normalize_gemini_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    """Reduce Pydantic JSON Schema to Gemini's documented supported subset."""

    def normalize(value: Any, *, container: str | None = None) -> Any:
        if isinstance(value, Mapping):
            if container in {"$defs", "properties"}:
                return {str(key): normalize(item) for key, item in value.items()}
            return {
                str(key): normalize(item, container=str(key))
                for key, item in value.items()
                if key in _SUPPORTED_SCHEMA_KEYS
            }
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


class GeminiLLMProvider:
    """Gemini REST adapter using schema-constrained JSON responses."""

    endpoint_root = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str | None,
        timeout_seconds: float = 30.0,
        max_attempts: int = 2,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip().removeprefix("models/")
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max(1, max_attempts)
        self._client = client

    def _validate_configuration(self) -> None:
        if not self.api_key:
            raise LLMConfigurationError("LLM_API_KEY is required when LLM_PROVIDER=gemini")
        if not self.model:
            raise LLMConfigurationError("LLM_MODEL is required when LLM_PROVIDER=gemini")

    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> ModelT:
        self._validate_configuration()
        prompt = self._build_prompt(task, system_prompt, context)
        request_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseFormat": {
                    "text": {
                        "mimeType": "application/json",
                        "schema": normalize_gemini_schema(output_schema.model_json_schema()),
                    }
                },
                "temperature": 0.2,
            },
        }
        url = f"{self.endpoint_root}/{self.model}:generateContent"
        last_error: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                if self._client is not None:
                    response = self._client.post(
                        url,
                        headers={"x-goog-api-key": self.api_key},
                        json=request_body,
                        timeout=self.timeout_seconds,
                    )
                else:
                    response = httpx.post(
                        url,
                        headers={"x-goog-api-key": self.api_key},
                        json=request_body,
                        timeout=self.timeout_seconds,
                    )
                response.raise_for_status()
                try:
                    return self._parse_response(response, output_schema)
                except LLMStructuredOutputError as exc:
                    logger.warning(
                        "Gemini returned invalid structured output task=%s model=%s attempt=%s/%s",
                        task,
                        self.model,
                        attempt,
                        self.max_attempts,
                    )
                    last_error = exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                self._log_provider_error(task, attempt, exc.response)
                if 400 <= status_code < 500 and status_code not in {408, 429}:
                    raise LLMProviderError(
                        "The LLM provider rejected the structured generation request"
                    ) from exc
                last_error = exc
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                logger.warning(
                    "Gemini transient request failure task=%s model=%s attempt=%s/%s error_type=%s",
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
        category = "request" if 400 <= response.status_code < 500 else "transient"
        logger.warning(
            "Gemini %s failure task=%s model=%s status=%s attempt=%s/%s provider_body=%s",
            category,
            task,
            self.model,
            response.status_code,
            attempt,
            self.max_attempts,
            serialized,
        )

    @staticmethod
    def _build_prompt(task: str, system_prompt: str, context: Mapping[str, Any]) -> str:
        serialized_context = json.dumps(context, ensure_ascii=False, separators=(",", ":"))
        return (
            f"{system_prompt}\n\nTask: {task}\n"
            "Use only the supplied structured context. Return only the requested structured result.\n"
            f"Context JSON:\n{serialized_context}"
        )

    @staticmethod
    def _parse_response(response: httpx.Response, output_schema: type[ModelT]) -> ModelT:
        try:
            body = response.json()
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            return output_schema.model_validate_json(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise LLMStructuredOutputError(
                "The LLM provider returned invalid structured output"
            ) from exc
