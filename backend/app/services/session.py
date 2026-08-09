from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.memory.base import MemoryObservation, MemoryService, NoopMemoryService
from app.models.interview import InterviewSession, InterviewTurn
from app.schemas.interview import (
    ChallengeMetadata,
    Feedback,
    IntegrityTelemetryEvent,
    InterviewHistoryDetail,
    InterviewHistoryItem,
    InterviewProgress,
    InterviewResponse,
    InterviewTranscriptMessage,
)
from app.schemas.workspace import SerializedWorkspace
from app.services.interviewer import InterviewEngine, InterviewEngineResult, InterviewStatePatch

logger = logging.getLogger(__name__)

PUBLIC_EVALUATOR_CANDIDATE: dict[str, Any] = {
    "member": {
        "id": "PUBLIC-EVALUATOR",
        "name": "Public evaluator",
        "jobRole": "Technical candidate",
        "yearsExperience": 0,
        "education": None,
        "status": "evaluation",
    },
    "missions": [],
    "signals": {
        "commitDays": 0,
        "missionsCompleted": 0,
        "missionsFirstTry": 0,
    },
}


def utcnow() -> datetime:
    return datetime.now(UTC)


class InterviewSessionError(Exception):
    status_code = 500
    code = "interview_session_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class SessionNotFoundError(InterviewSessionError):
    status_code = 404
    code = "session_not_found"


class SessionAlreadyExistsError(InterviewSessionError):
    status_code = 409
    code = "session_already_exists"


class SessionCompletedError(InterviewSessionError):
    status_code = 409
    code = "session_completed"


class InterviewSessionRepository:
    """Persistence boundary for exact interview session state and transcript turns."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, session_id: str) -> InterviewSession | None:
        statement = select(InterviewSession).where(InterviewSession.session_id == session_id)
        return self.db.scalar(statement)

    def get_for_owner(self, session_id: str, owner_id: str) -> InterviewSession | None:
        statement = select(InterviewSession).where(
            InterviewSession.session_id == session_id,
            InterviewSession.owner_id == owner_id,
        )
        return self.db.scalar(statement)

    def list_for_owner(self, owner_id: str, *, limit: int = 50) -> list[InterviewSession]:
        statement = (
            select(InterviewSession)
            .where(InterviewSession.owner_id == owner_id)
            .order_by(InterviewSession.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def add_session(self, session: InterviewSession) -> None:
        self.db.add(session)

    def flush(self) -> None:
        self.db.flush()

    def add_turn(
        self,
        session_id: str,
        *,
        role: str,
        content: str,
        kind: str = "message",
        payload: dict[str, Any] | None = None,
    ) -> InterviewTurn:
        sequence_statement = select(func.coalesce(func.max(InterviewTurn.sequence), 0)).where(
            InterviewTurn.session_id == session_id
        )
        next_sequence = int(self.db.scalar(sequence_statement) or 0) + 1
        turn = InterviewTurn(
            session_id=session_id,
            sequence=next_sequence,
            role=role,
            kind=kind,
            content=content,
            payload=payload,
        )
        self.db.add(turn)
        self.db.flush()
        return turn

    def list_turns(self, session_id: str) -> list[InterviewTurn]:
        statement = (
            select(InterviewTurn)
            .where(InterviewTurn.session_id == session_id)
            .order_by(InterviewTurn.sequence)
        )
        return list(self.db.scalars(statement).all())

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, session: InterviewSession) -> None:
        self.db.refresh(session)


class InterviewSessionService:
    """Application service coordinating persistence and the replaceable interview engine."""

    def __init__(
        self,
        repository: InterviewSessionRepository,
        engine: InterviewEngine,
        memory: MemoryService | None = None,
    ) -> None:
        self.repository = repository
        self.engine = engine
        self.memory = memory or NoopMemoryService()

    def start(
        self,
        session_id: str,
        candidate: dict[str, Any],
        workspace: SerializedWorkspace | None = None,
        owner_id: str | None = None,
        integrity_events: list[IntegrityTelemetryEvent] | None = None,
    ) -> InterviewResponse:
        if self.repository.get(session_id) is not None:
            raise SessionAlreadyExistsError(f"Session '{session_id}' already exists")

        candidate_data = candidate or PUBLIC_EVALUATOR_CANDIDATE

        session = InterviewSession(
            session_id=session_id,
            candidate_data=candidate_data,
            owner_id=owner_id,
            integrity_telemetry=self._serialize_integrity_events(integrity_events),
        )
        self.repository.add_session(session)
        try:
            self.repository.flush()
        except IntegrityError as exc:
            self.repository.rollback()
            raise SessionAlreadyExistsError(f"Session '{session_id}' already exists") from exc

        try:
            result = (
                self.engine.start(session, workspace=workspace)
                if workspace is not None
                else self.engine.start(session)
            )
            self._apply_engine_result(session, result)
            self.repository.add_turn(
                session_id,
                role="interviewer",
                kind=result.turn_kind,
                content=result.reply,
                payload=result.turn_payload,
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        self.repository.refresh(session)
        self._write_memory(session, result.memory_observations)
        return self._to_response(session, result)

    def continue_session(
        self,
        session_id: str,
        message: str,
        workspace: SerializedWorkspace | None = None,
        owner_id: str | None = None,
        integrity_events: list[IntegrityTelemetryEvent] | None = None,
    ) -> InterviewResponse:
        session = self.repository.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id}' does not exist")
        if session.owner_id is not None and session.owner_id != owner_id:
            raise SessionNotFoundError(f"Session '{session_id}' does not exist")
        if session.status == "completed":
            raise SessionCompletedError(f"Session '{session_id}' is already completed")

        candidate_payload = (
            {"workspace": workspace.model_dump(mode="json", by_alias=True, exclude_none=True)}
            if workspace is not None
            else None
        )
        try:
            if integrity_events:
                session.integrity_telemetry = [
                    *session.integrity_telemetry,
                    *self._serialize_integrity_events(integrity_events),
                ][-500:]
            self.repository.add_turn(
                session_id,
                role="candidate",
                content=message,
                payload=candidate_payload,
            )
            session.turn_count += 1
            session.updated_at = utcnow()

            conversation = self.repository.list_turns(session_id)
            result = (
                self.engine.respond(session, message, conversation, workspace=workspace)
                if workspace is not None
                else self.engine.respond(session, message, conversation)
            )
            self._apply_engine_result(session, result)
            self.repository.add_turn(
                session_id,
                role="interviewer",
                kind=result.turn_kind,
                content=result.reply,
                payload=result.turn_payload,
            )
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        self.repository.refresh(session)
        self._write_memory(session, result.memory_observations)
        return self._to_response(session, result)

    @staticmethod
    def _serialize_integrity_events(
        events: list[IntegrityTelemetryEvent] | None,
    ) -> list[dict[str, Any]]:
        return [event.model_dump(mode="json") for event in events or []]

    def _write_memory(
        self,
        session: InterviewSession,
        observations: list[MemoryObservation],
    ) -> None:
        member = session.candidate_data.get("member")
        candidate_id = str(member.get("id", "unknown")) if isinstance(member, dict) else "unknown"
        for observation in observations:
            try:
                self.memory.write_observation(
                    session_id=session.session_id,
                    candidate_id=candidate_id,
                    observation=observation,
                )
            except Exception as exc:  # noqa: BLE001 - SQL success must survive memory outages
                logger.warning(
                    "Interview memory write failed session=%s candidate=%s error_type=%s",
                    session.session_id,
                    candidate_id,
                    type(exc).__name__,
                )

    @staticmethod
    def _apply_engine_result(session: InterviewSession, result: InterviewEngineResult) -> None:
        InterviewSessionService._apply_state_patch(session, result.state_patch)
        session.updated_at = utcnow()

        if result.done:
            session.status = "completed"
            session.completed_at = utcnow()
            feedback = result.feedback
            if feedback is not None:
                completion_state = dict(session.completion_state)
                completion_state["feedback"] = feedback.model_dump()
                session.completion_state = completion_state

    @staticmethod
    def _apply_state_patch(session: InterviewSession, patch: InterviewStatePatch) -> None:
        for field_name in patch.model_fields_set:
            value = getattr(patch, field_name)
            setattr(session, field_name, value)

    @staticmethod
    def _to_response(
        session: InterviewSession,
        result: InterviewEngineResult,
    ) -> InterviewResponse:
        feedback: Feedback | None = result.feedback
        plan = session.completion_state.get("interviewPlan", {})
        minimum_questions = int(plan.get("minimumQuestions", 8))
        minimum_days = int(plan.get("minimumDays", 4))
        challenge = (
            ChallengeMetadata.model_validate(session.current_challenge)
            if session.current_challenge is not None
            else None
        )
        progress = InterviewProgress(
            questionsAsked=session.question_count,
            minimumQuestions=minimum_questions,
            daysCovered=len(set(session.covered_curriculum_days)),
            minimumDays=minimum_days,
        )
        return InterviewResponse(
            reply=result.reply,
            done=result.done,
            feedback=feedback,
            challenge=challenge,
            progress=progress,
        )

    def list_history(self, owner_id: str) -> list[InterviewHistoryItem]:
        return [self._to_history_item(session) for session in self.repository.list_for_owner(owner_id)]

    def get_history(self, owner_id: str, session_id: str) -> InterviewHistoryDetail:
        session = self.repository.get_for_owner(session_id, owner_id)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id}' does not exist")
        turns = self.repository.list_turns(session_id)
        item = self._to_history_item(session)
        challenge = (
            ChallengeMetadata.model_validate(session.current_challenge)
            if session.current_challenge is not None
            else None
        )
        feedback_value = session.completion_state.get("feedback")
        feedback = Feedback.model_validate(feedback_value) if feedback_value is not None else None
        plan = session.completion_state.get("interviewPlan", {})
        return InterviewHistoryDetail(
            **item.model_dump(),
            candidate=session.candidate_data,
            challenge=challenge,
            progress=InterviewProgress(
                questionsAsked=session.question_count,
                minimumQuestions=int(plan.get("minimumQuestions", 8)),
                daysCovered=len(set(session.covered_curriculum_days)),
                minimumDays=int(plan.get("minimumDays", 4)),
            ),
            feedback=feedback,
            messages=[
                InterviewTranscriptMessage(
                    sequence=turn.sequence,
                    role=turn.role,
                    text=turn.content,
                )
                for turn in turns
                if turn.role in {"interviewer", "candidate"}
            ],
        )

    @staticmethod
    def _to_history_item(session: InterviewSession) -> InterviewHistoryItem:
        member = session.candidate_data.get("member", {})
        return InterviewHistoryItem(
            sessionId=session.session_id,
            status=session.status,
            candidateName=str(member.get("name", "Candidate")),
            candidateRole=str(member.get("jobRole", "Technical candidate")),
            createdAt=session.created_at,
            lastActivity=session.updated_at,
            completedAt=session.completed_at,
            questionsAsked=session.question_count,
            daysCovered=len(set(session.covered_curriculum_days)),
            currentTopic=session.current_topic,
            resultAvailable=session.status == "completed"
            and "feedback" in session.completion_state,
        )
