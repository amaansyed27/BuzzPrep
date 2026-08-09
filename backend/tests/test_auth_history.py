from __future__ import annotations

from collections.abc import Mapping

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth.base import AuthenticatedUser, AuthError
from app.auth.supabase import SupabaseAuthService
from app.interview.engine import AdaptiveInterviewEngine
from app.llm.fake import FakeLLMProvider
from app.main import create_app
from app.profiling.loader import load_candidates


def candidate() -> dict:
    return load_candidates()[0].model_dump(mode="json", by_alias=True)


class FakeAuthService:
    users: Mapping[str, AuthenticatedUser] = {
        "token-a": AuthenticatedUser(user_id="user-a", email="a@example.com"),
        "token-b": AuthenticatedUser(user_id="user-b", email="b@example.com"),
    }

    def verify_token(self, access_token: str) -> AuthenticatedUser:
        try:
            return self.users[access_token]
        except KeyError as exc:
            raise AuthError("The authentication token is invalid or expired") from exc


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_public_interview_remains_unauthenticated_with_auth_configured(tmp_path) -> None:
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'public.db'}",
        interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
        auth_service=FakeAuthService(),
    )

    with TestClient(app) as client:
        started = client.post(
            "/api/interview",
            json={"sessionId": "public-session", "candidate": candidate()},
        )
        continued = client.post(
            "/api/interview",
            json={"sessionId": "public-session", "message": "public evaluator answer"},
        )

    assert started.status_code == 200
    assert continued.status_code == 200


def test_authenticated_history_is_owned_and_isolated(tmp_path) -> None:
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'owned.db'}",
        interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
        auth_service=FakeAuthService(),
    )

    with TestClient(app) as client:
        started = client.post(
            "/api/interview",
            headers=auth_headers("token-a"),
            json={"sessionId": "owned-a", "candidate": candidate()},
        )
        assert started.status_code == 200

        continued = client.post(
            "/api/interview",
            headers=auth_headers("token-a"),
            json={"sessionId": "owned-a", "message": "owned answer with trade-off"},
        )
        assert continued.status_code == 200

        owner_history = client.get(
            "/api/me/interviews",
            headers=auth_headers("token-a"),
        )
        other_history = client.get(
            "/api/me/interviews",
            headers=auth_headers("token-b"),
        )
        owner_detail = client.get(
            "/api/me/interviews/owned-a",
            headers=auth_headers("token-a"),
        )
        other_detail = client.get(
            "/api/me/interviews/owned-a",
            headers=auth_headers("token-b"),
        )
        anonymous_continue = client.post(
            "/api/interview",
            json={"sessionId": "owned-a", "message": "must not load an owned session"},
        )

    assert owner_history.status_code == 200
    assert len(owner_history.json()["interviews"]) == 1
    assert owner_history.json()["interviews"][0]["sessionId"] == "owned-a"
    assert owner_history.json()["interviews"][0]["questionsAsked"] == 2
    assert other_history.json() == {"interviews": []}
    assert owner_detail.status_code == 200
    assert owner_detail.json()["candidate"]["member"]["id"] == "CAND-001"
    assert [message["role"] for message in owner_detail.json()["messages"]] == [
        "interviewer",
        "candidate",
        "interviewer",
    ]
    assert other_detail.status_code == 404
    assert anonymous_continue.status_code == 404


def test_history_requires_valid_authentication(tmp_path) -> None:
    app = create_app(
        database_url=f"sqlite:///{tmp_path / 'auth-required.db'}",
        interview_engine=AdaptiveInterviewEngine(FakeLLMProvider()),
        auth_service=FakeAuthService(),
    )

    with TestClient(app) as client:
        missing = client.get("/api/me/interviews")
        malformed = client.get(
            "/api/me/interviews",
            headers={"Authorization": "Token not-bearer"},
        )
        invalid = client.get(
            "/api/me/interviews",
            headers=auth_headers("invalid"),
        )

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "authentication_required"
    assert malformed.status_code == 401
    assert invalid.status_code == 401


def test_supabase_auth_service_validates_user_without_exposing_key() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["authorization"]
        captured["apikey"] = request.headers["apikey"]
        return httpx.Response(
            200,
            request=request,
            json={"id": "supabase-user", "email": "person@example.com"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        service = SupabaseAuthService(
            url="https://project.supabase.co",
            publishable_key="public-test-key",
            client=client,
        )
        user = service.verify_token("access-token")

    assert user == AuthenticatedUser(user_id="supabase-user", email="person@example.com")
    assert captured == {
        "authorization": "Bearer access-token",
        "apikey": "public-test-key",
    }


def test_supabase_auth_service_rejects_expired_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, request=request, json={"message": "expired"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        service = SupabaseAuthService(
            url="https://project.supabase.co",
            publishable_key="public-test-key",
            client=client,
        )
        with pytest.raises(AuthError, match="invalid or expired"):
            service.verify_token("expired-token")
