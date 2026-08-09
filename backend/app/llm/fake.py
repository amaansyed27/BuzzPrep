from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from app.interview.models import (
    AdaptiveAction,
    AdaptiveDecision,
    AnswerStrength,
    FinalFeedbackOutput,
    GeneratedInterviewQuestion,
    QuestionKind,
    TurnEvaluation,
    WorkspaceConsistency,
)
from app.llm.base import LLMStructuredOutputError, ModelT


class FakeLLMProvider:
    """Deterministic provider for tests and key-free local development.

    Scripted outputs may be supplied per task. Unscripted calls use small deterministic
    rules so the full interview remains runnable without network access.
    """

    def __init__(self, scripted: Mapping[str, list[BaseModel | dict[str, Any]]] | None = None) -> None:
        self._scripted = {
            task: deque(values) for task, values in (scripted or {}).items()
        }
        self.calls: list[dict[str, Any]] = []
        self.task_counts: defaultdict[str, int] = defaultdict(int)

    def generate_structured(
        self,
        *,
        task: str,
        system_prompt: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> ModelT:
        self.calls.append(
            {
                "task": task,
                "system_prompt": system_prompt,
                "context": dict(context),
                "output_schema": output_schema.__name__,
            }
        )
        self.task_counts[task] += 1

        scripted = self._scripted.get(task)
        if scripted:
            raw = scripted.popleft()
            try:
                if isinstance(raw, BaseModel):
                    return output_schema.model_validate(raw.model_dump(mode="json"))
                return output_schema.model_validate(raw)
            except ValidationError as exc:
                raise LLMStructuredOutputError(
                    f"Fake provider returned invalid structured output for {task}"
                ) from exc

        value = self._default_output(task, context, output_schema)
        try:
            return output_schema.model_validate(value)
        except ValidationError as exc:
            raise LLMStructuredOutputError(
                f"Fake provider could not produce valid structured output for {task}"
            ) from exc

    def _default_output(
        self,
        task: str,
        context: Mapping[str, Any],
        output_schema: type[ModelT],
    ) -> dict[str, Any]:
        if output_schema is TurnEvaluation:
            return self._evaluation(context)
        if output_schema is AdaptiveDecision:
            return self._decision(context)
        if output_schema is GeneratedInterviewQuestion:
            return self._question(context)
        if output_schema is FinalFeedbackOutput:
            return self._feedback(context)
        raise LLMStructuredOutputError(f"No fake output rule is registered for task '{task}'")

    @staticmethod
    def _evaluation(context: Mapping[str, Any]) -> dict[str, Any]:
        answer = str(context.get("candidate_answer", "")).strip()
        normalized = answer.lower()
        workspace_facts = list(context.get("workspace_facts") or [])

        if not answer or normalized in {"i don't know", "idk", "not sure", "unsure"}:
            strength = AnswerStrength.UNCLEAR
            score = 0.2
        elif any(token in normalized for token in ("because", "trade-off", "tradeoff", "however")):
            strength = AnswerStrength.STRONG
            score = 0.9
        elif len(answer.split()) >= 10:
            strength = AnswerStrength.ADEQUATE
            score = 0.7
        else:
            strength = AnswerStrength.WEAK
            score = 0.4

        return {
            "strength": strength,
            "correctness": score,
            "reasoning_quality": score,
            "trade_off_awareness": 0.9 if strength is AnswerStrength.STRONG else score,
            "practical_understanding": score,
            "workspace_consistency": (
                WorkspaceConsistency.CONSISTENT
                if workspace_facts
                else WorkspaceConsistency.NOT_APPLICABLE
            ),
            "missing_points": [] if strength is AnswerStrength.STRONG else ["Add one concrete justification"],
            "follow_up_recommendation": (
                "Probe a trade-off or impose a constraint"
                if strength is AnswerStrength.STRONG
                else "Ask for a concrete clarification or prerequisite explanation"
            ),
        }

    @staticmethod
    def _decision(context: Mapping[str, Any]) -> dict[str, Any]:
        evaluation = context.get("evaluation") or {}
        strength = evaluation.get("strength")
        if strength == AnswerStrength.STRONG or strength == AnswerStrength.STRONG.value:
            return {
                "action": AdaptiveAction.DEEPEN,
                "reason": "The answer is strong enough for a deeper constraint.",
                "focus": "trade-offs and failure modes",
                "constraint": "Assume latency and cost now matter equally.",
            }
        if strength in {AnswerStrength.WEAK, AnswerStrength.UNCLEAR, "weak", "unclear"}:
            return {
                "action": AdaptiveAction.FOLLOW_UP,
                "reason": "The answer needs a targeted diagnostic probe.",
                "focus": "the missing prerequisite or justification",
            }
        return {
            "action": AdaptiveAction.TRANSITION,
            "reason": "The answer is adequate; continue through the planned coverage.",
            "focus": "the next planned objective",
        }

    @staticmethod
    def _question(context: Mapping[str, Any]) -> dict[str, Any]:
        area = context.get("planned_area") or {}
        topic = str(area.get("topic", "the current topic"))
        day = area.get("day", "?")
        intent = str(area.get("intent", "assessment"))
        decision = context.get("adaptive_decision") or {}
        action = decision.get("action")
        previous_answer = str(context.get("candidate_answer", "")).strip()
        workspace_facts = list(context.get("workspace_facts") or [])

        workspace_fact = str(workspace_facts[-1]) if workspace_facts else None
        prefix = f"Day {day} — {topic}:"

        if workspace_fact:
            question = f"{prefix} You {workspace_fact}. Why did you make that choice, and what trade-off did it introduce?"
            kind = QuestionKind.FOLLOW_UP
        elif action in {AdaptiveAction.DEEPEN, AdaptiveAction.DEEPEN.value}:
            snippet = previous_answer[:80]
            question = (
                f"{prefix} You said '{snippet}'. Now add a constraint: how would your design change, "
                "and which trade-off would you accept?"
            )
            kind = QuestionKind.DEEPER
        elif action in {AdaptiveAction.FOLLOW_UP, AdaptiveAction.FOLLOW_UP.value}:
            snippet = previous_answer[:80] or "your last answer"
            question = (
                f"{prefix} Clarify '{snippet}': what is the key prerequisite concept, and how would "
                "you verify it in practice?"
            )
            kind = QuestionKind.DIAGNOSTIC
        elif context.get("question_count", 0) == 0:
            question = f"{prefix} Explain how you would approach this area and justify your first engineering choice."
            kind = QuestionKind.INITIAL
        else:
            question = (
                f"{prefix} Walk through a practical approach for this planned {intent} area and explain "
                "the most important engineering trade-off."
            )
            kind = QuestionKind.TRANSITION

        return {
            "question": question,
            "kind": kind,
            "challenge_summary": f"Assess {topic} using the planned {intent} intent.",
            "workspace_fact_used": workspace_fact,
        }

    @staticmethod
    def _feedback(context: Mapping[str, Any]) -> dict[str, Any]:
        evaluations = list(context.get("evaluations") or [])
        candidate = context.get("profile") or {}
        name = candidate.get("name", "The candidate")
        strong_days = [str(item.get("day")) for item in evaluations if item.get("strength") == "strong"]
        weak_days = [
            str(item.get("day"))
            for item in evaluations
            if item.get("strength") in {"weak", "unclear"}
        ]
        strengths = (
            [f"Strong reasoning on curriculum day(s) {', '.join(strong_days[:3])}"]
            if strong_days
            else ["Completed the required multi-area technical interview"]
        )
        gaps = (
            [f"Needs deeper justification on curriculum day(s) {', '.join(weak_days[:3])}"]
            if weak_days
            else ["Continue making trade-offs explicit when explaining design choices"]
        )
        return {
            "summary": f"{name} completed a curriculum-grounded interview across multiple planned areas.",
            "strengths": strengths,
            "gaps": gaps,
            "next": ["Review the weakest assessed area and practice explaining one concrete trade-off."],
        }
