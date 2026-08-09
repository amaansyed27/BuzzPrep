from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str | None = None


class AuthError(Exception):
    status_code = 401
    code = "invalid_auth_token"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthenticationRequiredError(AuthError):
    code = "authentication_required"


class AuthUnavailableError(AuthError):
    status_code = 503
    code = "auth_unavailable"


class AuthService(Protocol):
    def verify_token(self, access_token: str) -> AuthenticatedUser: ...


class UnconfiguredAuthService:
    def verify_token(self, access_token: str) -> AuthenticatedUser:
        raise AuthUnavailableError("Authentication is not configured")
