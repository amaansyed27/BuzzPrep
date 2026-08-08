from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.interview import InterviewSession, InterviewTurn
from app.schemas.interview import Feedback, InterviewResponse
from app.services.interviewer import InterviewEngine, InterviewEngineResult, InterviewStatePatch


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


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

    def __init__(self, repository: InterviewSessionRepository, engine: InterviewEngine) -> None:
        self.repository = repository
        self.engine = engine

    def start(self, session_id: str, candidate: dict[str, Any]) -> InterviewResponse:
        if self.repository.get(session_id) is not None:
            raise SessionAlreadyExistsError(f"Session '{session_id}' already exists")

        session = InterviewSession(session_id=session_id, candidate_data=candidate)
        self.repository.add_session(session)
        try:
            self.repository.flush()
        except IntegrityError as exc:
            self.repository.rollback()
            raise SessionAlreadyExistsError(f"Session '{session_id}' already exists") from exc

        result = self.engine.start(session)
        self._apply_engine_result(session, result)
        self.repository.add_turn(
            session_id,
            role="interviewer",
            kind=result.turn_kind,
            content=result.reply,
        )

        try:
            self.repository.commit()
        except IntegrityError as exc:
            self.repository.rollback()
            raise SessionAlreadyExistsError(f"Session '{session_id}' already exists") from exc

        self.repository.refresh(session)
        return self._to_response(result)

    def continue_session(self, session_id: str, message: str) -> InterviewResponse:
        session = self.repository.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id}' does not exist")
        if session.status == "completed":
            raise SessionCompletedError(f"Session '{session_id}' is already completed")

        self.repository.add_turn(session_id, role="candidate", content=message)
        session.turn_count += 1
        session.updated_at = utcnow()

        conversation = self.repository.list_turns(session_id)
        result = self.engine.respond(session, message, conversation)
        self._apply_engine_result(session, result)
        self.repository.add_turn(
            session_id,
            role="interviewer",
            kind=result.turn_kind,
            content=result.reply,
        )
        self.repository.commit()
        self.repository.refresh(session)
        return self._to_response(result)

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
    def _to_response(result: InterviewEngineResult) -> InterviewResponse:
        feedback: Feedback | None = result.feedback
        return InterviewResponse(reply=result.reply, done=result.done, feedback=feedback)
