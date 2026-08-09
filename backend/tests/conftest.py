from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("LLM_PROVIDER", "fake")
os.environ.setdefault("BREETH_ENABLED", "false")

from app.interview.engine import AdaptiveInterviewEngine
from app.llm.fake import FakeLLMProvider
from app.main import create_app
from app.memory.fake import InMemoryMemoryService


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'buzzprep-test.db'}"


@pytest.fixture
def fake_provider() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
def client(database_url: str, fake_provider: FakeLLMProvider) -> Iterator[TestClient]:
    memory = InMemoryMemoryService()
    app = create_app(
        database_url=database_url,
        interview_engine=AdaptiveInterviewEngine(fake_provider, memory),
        memory_service=memory,
    )
    with TestClient(app) as test_client:
        yield test_client
