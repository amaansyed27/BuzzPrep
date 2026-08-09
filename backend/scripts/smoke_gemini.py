from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import load_environment
from app.interview.engine import AdaptiveInterviewEngine
from app.llm.gemini import GeminiLLMProvider
from app.memory.base import NoopMemoryService
from app.profiling.loader import load_candidates

STRONG_ANSWER = """I would start with a measured baseline, then separate retrieval quality
from generation quality. For retrieval I would track recall at k against a labelled set, tune
chunking and filters, and compare exact versus approximate search. For production I would bound
latency with timeouts, cache stable embeddings, and use a fallback path. I would only accept a
higher recall configuration if its p95 latency and cost stay inside the service objective."""

WEAK_ANSWER = "I would use the default settings because they are probably fast enough."


def _safe_summary(payload: dict[str, object]) -> dict[str, object]:
    return {
        "done": payload.get("done"),
        "reply": payload.get("reply"),
        "challenge": payload.get("challenge"),
        "progress": payload.get("progress"),
    }


def main() -> int:
    load_environment()
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    if provider != "gemini" or not api_key or not model:
        print("BLOCKED: set LLM_PROVIDER=gemini, LLM_API_KEY, and LLM_MODEL in repo-root .env")
        return 2

    # Importing the ASGI module builds the configured production provider, so do it
    # only after the credential preflight has produced a clear, secret-safe result.
    from app.main import create_app

    session_id = f"gemini-smoke-{uuid.uuid4().hex[:10]}"
    candidate = load_candidates()[0].model_dump(by_alias=True)
    with tempfile.TemporaryDirectory(prefix="buzzprep-gemini-") as directory:
        database_path = Path(directory) / "smoke.db"
        application = create_app(
            database_url=f"sqlite:///{database_path.as_posix()}",
            interview_engine=AdaptiveInterviewEngine(
                GeminiLLMProvider(api_key=api_key, model=model),
                NoopMemoryService(),
            ),
            memory_service=NoopMemoryService(),
        )
        with TestClient(application) as client:
            responses: list[dict[str, object]] = []
            start = client.post(
                "/api/interview",
                json={"sessionId": session_id, "candidate": candidate},
            )
            start.raise_for_status()
            responses.append(_safe_summary(start.json()))

            for answer in (STRONG_ANSWER, WEAK_ANSWER):
                turn = client.post(
                    "/api/interview",
                    json={"sessionId": session_id, "message": answer},
                )
                turn.raise_for_status()
                responses.append(_safe_summary(turn.json()))

    print(
        json.dumps(
            {
                "status": "PASS",
                "provider": provider,
                "model": model,
                "sessionId": session_id,
                "responses": responses,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
