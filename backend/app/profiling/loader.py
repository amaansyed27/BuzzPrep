from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.profiling.candidate import CandidateRecord

RESOURCE_ROOT = Path(__file__).resolve().parents[3] / "hackathon-resources"
DEFAULT_CANDIDATES_PATH = RESOURCE_ROOT / "candidates.json"


class CandidateCollection(BaseModel):
    candidates: list[CandidateRecord] = Field(min_length=1)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def load_candidates(path: str | Path | None = None) -> list[CandidateRecord]:
    """Load and validate candidate records from the supplied resource or a test fixture."""
    source_path = Path(path) if path is not None else DEFAULT_CANDIDATES_PATH
    collection = CandidateCollection.model_validate(_read_json(source_path))
    return collection.candidates
