from __future__ import annotations

import logging
from typing import Any

import httpx

from app.auth.base import AuthenticatedUser, AuthError, AuthUnavailableError

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """Validate Supabase access tokens against the hosted Auth service."""

    def __init__(
        self,
        *,
        url: str,
        publishable_key: str,
        timeout_seconds: float = 8.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.url = url.rstrip("/")
        self.publishable_key = publishable_key.strip()
        self.timeout_seconds = timeout_seconds
        self._client = client

    def verify_token(self, access_token: str) -> AuthenticatedUser:
        token = access_token.strip()
        if not token:
            raise AuthError("The authentication token is invalid or expired")

        headers = {
            "apikey": self.publishable_key,
            "Authorization": f"Bearer {token}",
        }
        try:
            response = (
                self._client.get(
                    f"{self.url}/auth/v1/user",
                    headers=headers,
                    timeout=self.timeout_seconds,
                )
                if self._client is not None
                else httpx.get(
                    f"{self.url}/auth/v1/user",
                    headers=headers,
                    timeout=self.timeout_seconds,
                )
            )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning("Supabase Auth verification unavailable error_type=%s", type(exc).__name__)
            raise AuthUnavailableError("Authentication is temporarily unavailable") from exc

        if response.status_code in {401, 403}:
            raise AuthError("The authentication token is invalid or expired")
        if response.status_code >= 400:
            logger.warning("Supabase Auth verification failed status=%s", response.status_code)
            raise AuthUnavailableError("Authentication is temporarily unavailable")

        try:
            body: Any = response.json()
            user_id = str(body["id"]).strip()
            email = body.get("email")
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthUnavailableError("Authentication returned an invalid user response") from exc
        if not user_id:
            raise AuthUnavailableError("Authentication returned an invalid user response")
        return AuthenticatedUser(
            user_id=user_id,
            email=str(email) if email is not None else None,
        )
