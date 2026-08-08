from __future__ import annotations

import json
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
                        "schema": output_schema.model_json_schema(),
                    }
                }
            },
        }
        url = f"{self.endpoint_root}/{self.model}:generateContent"
        last_error: Exception | None = None

        for _ in range(self.max_attempts):
            try:
                if self._client is not None:
                    response = self._client.post(
                        url,
                        headers={"x-goog-api-key": self.api_key},
                        json=request_body,
                    )
                else:
                    response = httpx.post(
                        url,
                        headers={"x-goog-api-key": self.api_key},
                        json=request_body,
                        timeout=self.timeout_seconds,
                    )
                response.raise_for_status()
                return self._parse_response(response, output_schema)
            except LLMStructuredOutputError:
                raise
            except httpx.HTTPStatusError as exc:
                if 400 <= exc.response.status_code < 500 and exc.response.status_code != 429:
                    raise LLMProviderError(
                        "The LLM provider rejected the structured generation request"
                    ) from exc
                last_error = exc
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc

        raise LLMProviderError("The configured LLM provider is unavailable") from last_error

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
