from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.config import load_environment
from app.llm.base import LLMConfigurationError
from app.llm.factory import build_llm_provider
from app.llm.fake import FakeLLMProvider


def test_root_env_loading_preserves_process_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "LLM_PROVIDER=gemini\nLLM_MODEL=from-dotenv\nDATABASE_URL=sqlite:///from-dotenv.db\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LLM_MODEL", "from-process")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert load_environment(env_path) is True
    assert os.environ["LLM_MODEL"] == "from-process"
    assert os.environ["DATABASE_URL"] == "sqlite:///from-dotenv.db"


def test_missing_provider_never_silently_selects_fake(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    with pytest.raises(LLMConfigurationError, match="LLM_PROVIDER is required"):
        build_llm_provider()


def test_fake_provider_requires_explicit_selection() -> None:
    assert isinstance(build_llm_provider(provider_name="fake"), FakeLLMProvider)
