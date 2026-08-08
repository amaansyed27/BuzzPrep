from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any, Literal

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from app.curriculum.loader import load_curriculum
from app.interview.graph_state import InterviewGraphState
from app.interview.models import (
    AdaptiveDecision,
    FinalFeedbackOutput,
    GeneratedInterviewQuestion,
    TurnEvaluation,
)
from app.interview.prompts import (
    ADAPT_SYSTEM_PROMPT,
    EVALUATION_SYSTEM_PROMPT,
    FEEDBACK_SYSTEM_PROMPT,
    QUESTION_SYSTEM_PROMPT,
)
from app.llm.base import LLMError, LLMProvider, LLMStructuredOutputError
from app.models.interview import InterviewSession, InterviewTurn
from app.planning.interview import build_interview_plan
from app.planning.models import MINIMUM_DAYS, MINIMUM_QUESTIONS, InterviewPlan, PlannedArea
from app.profiling.candidate import CandidateProfile, profile_candidate
from app.schemas.interview import Feedback
from app.schemas.workspace import SerializedWorkspace, WorkspaceEvent
from app.services.interviewer import (
    InterviewEngineResult,
    InterviewInputError,
    InterviewProviderError,
    InterviewStatePatch,
)

PROFILE_STATE_KEY = "candidateProfile"
PLAN_STATE_KEY = "interviewPlan"
EVALUATIONS_STATE_KEY = "turnEvaluations"
MINIMUM_QUESTION_COUNT = MINIMUM_QUESTIONS
MINIMUM_COVERED_DAYS = MINIMUM_DAYS


def completion_eligible(question_count: int, covered_days: Sequence[int]) -> bool:
    """Hard completion invariant. The LLM never controls this decision."""
    return question_count >= MINIMUM_QUESTION_COUNT and len(set(covered_days)) >= MINIMUM_COVERED_DAYS


def _event_fact(event: WorkspaceEvent) -> str:
    payload = event.payload
    if event.type == "add":
        return f"added node {payload.node_id}"
    if event.type == "remove":
        return f"removed node {payload.node_id}"
    if event.type == "connect":
        return f"connected {payload.source} to {payload.target}"
    if event.type == "disconnect":
        endpoints = (
            f" from {payload.source} to {payload.target}"
            if payload.source and payload.target
            else ""
        )
        return f"disconnected edge {payload.edge_id}{endpoints}"
    if event.type == "configure":
        return f"configured {payload.config_key} to {payload.value!r}"
    if event.type == "edit":
        return f"edited {payload.editor_id}"
    if event.type == "run":
        return f"ran {payload.target}"
    if event.type == "submit":
        return f"submitted task {payload.task_id}"
    if event.type == "undo":
        return "used undo"
    reason = f" ({payload.reason})" if payload.reason else ""
    return f"reset the workspace{reason}"


def workspace_facts(workspace: SerializedWorkspace | None) -> list[str]:
    if workspace is None:
        return []
    return [_event_fact(event) for event in workspace.events[-10:]]


def _workspace_context(workspace: SerializedWorkspace | None) -> dict[str, Any] | None:
    if workspace is None:
        return None
    data = workspace.model_dump(mode="json", by_alias=True, exclude_none=True)
    data.pop("initialSnapshot", None)
    data["events"] = data.get("events", [])[-20:]
    return data


def _profile_context(profile: CandidateProfile) -> dict[str, Any]:
    return {
        "candidate_id": profile.candidate_id,
        "name": profile.name,
        "job_role": profile.job_role,
        "years_experience": profile.years_experience,
        "education": profile.education,
        "experience_level": profile.experience_level.value,
        "passed_days": profile.passed_days,
        "failed_days": profile.failed_days,
        "skipped_days": profile.skipped_days,
        "strong_days": profile.strong_days,
        "weaker_days": profile.weaker_days,
    }


def _area_context(area: PlannedArea) -> dict[str, Any]:
    return area.model_dump(mode="json", by_alias=True)


def _transcript_context(conversation: Sequence[InterviewTurn], limit: int = 8) -> list[dict[str, Any]]:
    return [
        {"role": turn.role, "kind": turn.kind, "content": turn.content}
        for turn in conversation[-limit:]
    ]


def _question_counts_by_day(conversation: Sequence[InterviewTurn]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for turn in conversation:
        if turn.role != "interviewer" or turn.kind != "question" or not turn.payload:
            continue
        day = turn.payload.get("curriculumDay")
        if isinstance(day, int):
            counts[day] += 1
    return counts


class AdaptiveInterviewEngine:
    """LangGraph-controlled adaptive interviewer backed by the Issue #1 SQL state boundary."""

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm
        self.catalog = load_curriculum()
        self.graph = self._build_graph()

    def start(
        self,
        session: InterviewSession,
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult:
        return self._invoke(
            {
                "mode": "start",
                "session": session,
                "conversation": [],
                "workspace": workspace,
                "workspace_facts": workspace_facts(workspace),
            }
        )

    def respond(
        self,
        session: InterviewSession,
        message: str,
        conversation: Sequence[InterviewTurn],
        *,
        workspace: SerializedWorkspace | None = None,
    ) -> InterviewEngineResult:
        return self._invoke(
            {
                "mode": "respond",
                "session": session,
                "conversation": conversation,
                "candidate_answer": message,
                "workspace": workspace,
                "workspace_facts": workspace_facts(workspace),
            }
        )

    def _invoke(self, state: InterviewGraphState) -> InterviewEngineResult:
        try:
            final_state = self.graph.invoke(state)
        except ValidationError as exc:
            raise InterviewInputError("Candidate data does not match the supplied candidate schema") from exc
        except LLMError as exc:
            raise InterviewProviderError(str(exc)) from exc
        result = final_state.get("result")
        if result is None:
            raise InterviewProviderError("Interview graph did not produce a response")
        return result

    def _build_graph(self):
        graph = StateGraph(InterviewGraphState)
        graph.add_node("prepare", self._prepare)
        graph.add_node("evaluate_answer", self._evaluate_answer)
        graph.add_node("adaptive_decision", self._adaptive_decision)
        graph.add_node("completion_gate", self._completion_gate)
        graph.add_node("select_area", self._select_area)
        graph.add_node("generate_question", self._generate_question)
        graph.add_node("finalize_feedback", self._finalize_feedback)

        graph.add_edge(START, "prepare")
        graph.add_conditional_edges(
            "prepare",
            self._route_after_prepare,
            {"start": "select_area", "respond": "evaluate_answer"},
        )
        graph.add_edge("evaluate_answer", "adaptive_decision")
        graph.add_edge("adaptive_decision", "completion_gate")
        graph.add_conditional_edges(
            "completion_gate",
            self._route_after_completion_gate,
            {"continue": "select_area", "finish": "finalize_feedback"},
        )
        graph.add_edge("select_area", "generate_question")
        graph.add_edge("generate_question", END)
        graph.add_edge("finalize_feedback", END)
        return graph.compile()

    def _prepare(self, state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        if state["mode"] == "start":
            profile = profile_candidate(session.candidate_data)
            plan = build_interview_plan(profile, self.catalog)
        else:
            profile_payload = session.completion_state.get(PROFILE_STATE_KEY)
            plan_payload = session.completion_state.get(PLAN_STATE_KEY)
            if profile_payload is None or plan_payload is None:
                profile = profile_candidate(session.candidate_data)
                plan = build_interview_plan(profile, self.catalog)
            else:
                profile = CandidateProfile.model_validate(profile_payload)
                plan = InterviewPlan.model_validate(plan_payload)
        return {"profile": profile, "plan": plan}

    @staticmethod
    def _route_after_prepare(state: InterviewGraphState) -> Literal["start", "respond"]:
        return state["mode"]

    def _evaluate_answer(self, state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        plan = state["plan"]
        area = self._area_for_day(plan, session.current_curriculum_day)
        context = {
            "profile": _profile_context(state["profile"]),
            "planned_area": _area_context(area),
            "current_question": session.current_challenge or {},
            "candidate_answer": state.get("candidate_answer", ""),
            "transcript": _transcript_context(state.get("conversation", [])),
            "workspace_facts": state.get("workspace_facts", []),
            "workspace_evidence": _workspace_context(state.get("workspace")),
        }
        evaluation = self.llm.generate_structured(
            task="evaluate_answer",
            system_prompt=EVALUATION_SYSTEM_PROMPT,
            context=context,
            output_schema=TurnEvaluation,
        )
        return {"evaluation": evaluation, "current_area": area}

    def _adaptive_decision(self, state: InterviewGraphState) -> dict[str, Any]:
        context = {
            "planned_area": _area_context(state["current_area"]),
            "evaluation": state["evaluation"].model_dump(mode="json"),
            "question_count": state["session"].question_count,
            "covered_curriculum_days": state["session"].covered_curriculum_days,
            "minimum_questions": MINIMUM_QUESTION_COUNT,
            "minimum_days": MINIMUM_COVERED_DAYS,
        }
        decision = self.llm.generate_structured(
            task="adaptive_decision",
            system_prompt=ADAPT_SYSTEM_PROMPT,
            context=context,
            output_schema=AdaptiveDecision,
        )
        return {"adaptive_decision": decision}

    @staticmethod
    def _completion_gate(state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        return {
            "completion_eligible": completion_eligible(
                session.question_count,
                session.covered_curriculum_days,
            )
        }

    @staticmethod
    def _route_after_completion_gate(state: InterviewGraphState) -> Literal["continue", "finish"]:
        return "finish" if state["completion_eligible"] else "continue"

    def _select_area(self, state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        plan = state["plan"]
        conversation = state.get("conversation", [])
        covered = set(session.covered_curriculum_days)
        missing_days = max(0, MINIMUM_COVERED_DAYS - len(covered))
        questions_until_minimum = max(0, MINIMUM_QUESTION_COUNT - session.question_count)

        if missing_days and missing_days >= questions_until_minimum:
            uncovered = next((area for area in plan.plan if area.day not in covered), None)
            if uncovered is not None:
                return {"current_area": uncovered}

        decision = state.get("adaptive_decision")
        current_area = state.get("current_area")
        counts = _question_counts_by_day(conversation)
        if (
            decision is not None
            and current_area is not None
            and decision.action.value in {"follow_up", "deepen"}
            and counts[current_area.day] < current_area.question_budget
        ):
            return {"current_area": current_area}

        next_question_number = session.question_count + 1
        return {"current_area": self._scheduled_area(plan, next_question_number)}

    def _generate_question(self, state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        profile = state["profile"]
        plan = state["plan"]
        area = state["current_area"]
        facts = state.get("workspace_facts", [])
        context = {
            "profile": _profile_context(profile),
            "planned_area": _area_context(area),
            "question_count": session.question_count,
            "covered_curriculum_days": session.covered_curriculum_days,
            "candidate_answer": state.get("candidate_answer", ""),
            "evaluation": (
                state["evaluation"].model_dump(mode="json") if state.get("evaluation") else None
            ),
            "adaptive_decision": (
                state["adaptive_decision"].model_dump(mode="json")
                if state.get("adaptive_decision")
                else None
            ),
            "transcript": _transcript_context(state.get("conversation", [])),
            "workspace_facts": facts,
            "workspace_evidence": _workspace_context(state.get("workspace")),
        }
        generated = self.llm.generate_structured(
            task="generate_question",
            system_prompt=QUESTION_SYSTEM_PROMPT,
            context=context,
            output_schema=GeneratedInterviewQuestion,
        )
        if generated.workspace_fact_used is not None and generated.workspace_fact_used not in facts:
            raise LLMStructuredOutputError("The LLM referenced workspace evidence that was not supplied")

        question_count = session.question_count + 1
        covered_days = list(dict.fromkeys([*session.covered_curriculum_days, area.day]))
        challenge = {
            "curriculumDay": area.day,
            "topic": area.topic,
            "intent": area.intent.value,
            "difficulty": area.difficulty.value,
            "interactionTypes": [item.value for item in area.interaction_types],
            "questionKind": generated.kind.value,
            "challengeSummary": generated.challenge_summary,
        }
        completion_state = self._updated_completion_state(state, plan, profile)
        patch_values: dict[str, Any] = {
            "question_count": question_count,
            "covered_curriculum_days": covered_days,
            "current_curriculum_day": area.day,
            "current_topic": area.topic,
            "current_challenge": challenge,
            "structured_scores": self._scores_patch(state),
            "completion_state": completion_state,
        }
        workspace_patch = self._workspace_patch(state)
        if workspace_patch is not None:
            patch_values["workspace_snapshot"] = workspace_patch
        patch = InterviewStatePatch(**patch_values)
        result = InterviewEngineResult(
            reply=generated.question,
            state_patch=patch,
            turn_kind="question",
            turn_payload={
                "curriculumDay": area.day,
                "topic": area.topic,
                "intent": area.intent.value,
                "difficulty": area.difficulty.value,
                "questionKind": generated.kind.value,
            },
        )
        return {"result": result}

    def _finalize_feedback(self, state: InterviewGraphState) -> dict[str, Any]:
        session = state["session"]
        scores = self._scores_patch(state)
        evaluations = list(scores.get(EVALUATIONS_STATE_KEY, []))
        context = {
            "profile": _profile_context(state["profile"]),
            "planned_areas": [_area_context(area) for area in state["plan"].plan],
            "question_count": session.question_count,
            "covered_curriculum_days": session.covered_curriculum_days,
            "evaluations": evaluations,
            "transcript": _transcript_context(state.get("conversation", []), limit=16),
            "workspace_facts": state.get("workspace_facts", []),
        }
        generated = self.llm.generate_structured(
            task="final_feedback",
            system_prompt=FEEDBACK_SYSTEM_PROMPT,
            context=context,
            output_schema=FinalFeedbackOutput,
        )
        feedback = Feedback.model_validate(generated.model_dump(mode="json"))
        completion_state = self._updated_completion_state(
            state,
            state["plan"],
            state["profile"],
        )
        completion_state["completionEligible"] = True
        patch_values: dict[str, Any] = {
            "current_curriculum_day": None,
            "current_topic": None,
            "current_challenge": None,
            "structured_scores": scores,
            "completion_state": completion_state,
        }
        workspace_patch = self._workspace_patch(state)
        if workspace_patch is not None:
            patch_values["workspace_snapshot"] = workspace_patch
        result = InterviewEngineResult(
            reply="Interview completed.",
            done=True,
            feedback=feedback,
            state_patch=InterviewStatePatch(**patch_values),
            turn_kind="completion",
            turn_payload={"questionCount": session.question_count},
        )
        return {"result": result}

    @staticmethod
    def _area_for_day(plan: InterviewPlan, day: int | None) -> PlannedArea:
        if day is not None:
            for area in plan.plan:
                if area.day == day:
                    return area
        raise InterviewProviderError("Persisted interview state does not identify a planned curriculum area")

    @staticmethod
    def _scheduled_area(plan: InterviewPlan, question_number: int) -> PlannedArea:
        cursor = 0
        for area in plan.plan:
            cursor += area.question_budget
            if question_number <= cursor:
                return area
        return plan.plan[(question_number - 1) % len(plan.plan)]

    @staticmethod
    def _workspace_patch(state: InterviewGraphState) -> dict[str, Any] | None:
        workspace = state.get("workspace")
        if workspace is None:
            return None
        return workspace.model_dump(mode="json", by_alias=True, exclude_none=True)

    @staticmethod
    def _scores_patch(state: InterviewGraphState) -> dict[str, Any]:
        scores = dict(state["session"].structured_scores)
        evaluations = list(scores.get(EVALUATIONS_STATE_KEY, []))
        evaluation = state.get("evaluation")
        area = state.get("current_area")
        if evaluation is not None and area is not None:
            evaluations.append(
                {
                    "day": area.day,
                    **evaluation.model_dump(mode="json"),
                }
            )
        scores[EVALUATIONS_STATE_KEY] = evaluations
        return scores

    @staticmethod
    def _updated_completion_state(
        state: InterviewGraphState,
        plan: InterviewPlan,
        profile: CandidateProfile,
    ) -> dict[str, Any]:
        completion_state = dict(state["session"].completion_state)
        completion_state[PROFILE_STATE_KEY] = profile.model_dump(mode="json")
        completion_state[PLAN_STATE_KEY] = plan.model_dump(mode="json", by_alias=True)
        completion_state["completionEligible"] = bool(state.get("completion_eligible", False))
        decision = state.get("adaptive_decision")
        if decision is not None:
            completion_state["lastDecision"] = decision.model_dump(mode="json")
        return completion_state
