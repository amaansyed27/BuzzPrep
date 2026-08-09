from __future__ import annotations

import json
import os
from typing import Literal

from pydantic import BaseModel, Field

from app.config import load_environment
from app.llm.gemini import GeminiLLMProvider
from app.llm.openai_compatible import GroqLLMProvider, OpenRouterLLMProvider


class ProviderSmokeResult(BaseModel):
    question: str = Field(min_length=8)
    difficulty: Literal["intermediate", "advanced"]
    evidence_focus: str = Field(min_length=4)


def main() -> int:
    load_environment()
    providers = [
        (
            "gemini",
            os.getenv("LLM_MODEL", "gemini-3.6-flash"),
            GeminiLLMProvider(
                api_key=os.getenv("LLM_API_KEY"),
                model=os.getenv("LLM_MODEL", "gemini-3.6-flash"),
            ),
        ),
        (
            "groq",
            os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            GroqLLMProvider(
                api_key=os.getenv("GROQ_API_KEY"),
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            ),
        ),
        (
            "openrouter",
            os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            OpenRouterLLMProvider(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            ),
        ),
    ]
    results: list[dict[str, str]] = []
    for name, model, provider in providers:
        generated = provider.generate_structured(
            task="provider_live_smoke",
            system_prompt=(
                "You are BuzzPrep. Produce one concise technical interview question as JSON. "
                "Do not include hidden reasoning."
            ),
            context={
                "candidate_role": "Senior Data Engineer",
                "curriculum_day": 8,
                "topic": "Vector Databases Overview",
                "workspace_evidence": "Candidate changed top-k from 5 to 12 under a 150ms budget.",
            },
            output_schema=ProviderSmokeResult,
        )
        results.append(
            {
                "provider": name,
                "model": str(model),
                "status": "PASS",
                "difficulty": generated.difficulty,
            }
        )
    print(json.dumps({"status": "PASS", "providers": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
