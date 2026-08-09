from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ROOT_ENV_PATH = REPOSITORY_ROOT / ".env"


def load_environment(path: str | Path = ROOT_ENV_PATH) -> bool:
    """Load BuzzPrep's root .env without overriding the real process environment."""
    return load_dotenv(dotenv_path=path, override=False)


def configured_cors_origins() -> list[str]:
    """Return explicit browser origins; deployed origins are comma-separated."""
    value = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
