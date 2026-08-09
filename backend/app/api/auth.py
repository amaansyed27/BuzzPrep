from __future__ import annotations

from fastapi import Request

from app.auth.base import AuthenticatedUser, AuthenticationRequiredError, AuthError


def optional_authenticated_user(request: Request) -> AuthenticatedUser | None:
    authorization = request.headers.get("authorization")
    if authorization is None:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise AuthError("The authentication token is invalid or expired")
    return request.app.state.auth_service.verify_token(token)


def require_authenticated_user(request: Request) -> AuthenticatedUser:
    user = optional_authenticated_user(request)
    if user is None:
        raise AuthenticationRequiredError("Sign in to access interview history")
    return user
