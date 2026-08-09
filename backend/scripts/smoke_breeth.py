from __future__ import annotations

import os
import time
import uuid

from app.config import load_environment
from app.memory.base import MemoryObservation
from app.memory.breeth import BreethMemoryService


def main() -> int:
    load_environment()
    api_key = os.getenv("BREETH_API_KEY", "").strip()
    if not api_key:
        print("BLOCKED: set BREETH_API_KEY in repo-root .env")
        return 2

    token = uuid.uuid4().hex[:12]
    session_id = f"buzzprep-smoke-{token}"
    candidate_id = f"CAND-SMOKE-{token}"
    service = BreethMemoryService(api_key=api_key)
    service.write_observation(
        session_id=session_id,
        candidate_id=candidate_id,
        observation=MemoryObservation(
            day=16,
            turn_number=1,
            source="workspace",
            text=f"Candidate justified timeout and retry boundaries. Smoke token {token}.",
        ),
    )

    records = []
    for _ in range(5):
        records = service.retrieve_relevant(
            session_id=session_id,
            candidate_id=candidate_id,
            query=f"timeout retry boundaries {token}",
            limit=4,
        )
        if any(token in record.text for record in records):
            break
        time.sleep(2)

    if not any(token in record.text for record in records):
        print(f"FAIL: observation was not retrieved for scoped session {session_id}")
        return 1

    other_session_records = service.retrieve_relevant(
        session_id=f"{session_id}-other",
        candidate_id=candidate_id,
        query=token,
        limit=4,
    )
    if any(token in record.text for record in other_session_records):
        print("FAIL: observation leaked into a different group_id")
        return 1

    print(
        f"PASS: wrote and retrieved one scoped observation for {session_id}; "
        "different-session retrieval did not contain it"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
