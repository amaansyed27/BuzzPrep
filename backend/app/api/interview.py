from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.schemas.interview import ErrorResponse, InterviewRequest, InterviewResponse
from app.services.session import InterviewSessionRepository, InterviewSessionService

router = APIRouter()


def get_interview_session_service(request: Request) -> Iterator[InterviewSessionService]:
    database = request.app.state.database
    engine = request.app.state.interview_engine
    with database.session() as db:
        yield InterviewSessionService(InterviewSessionRepository(db), engine)


@router.post(
    "/api/interview",
    response_model=InterviewResponse,
    response_model_exclude_none=True,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def interview(
    payload: InterviewRequest,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewResponse:
    if payload.is_start:
        assert payload.candidate is not None
        return service.start(payload.sessionId, payload.candidate)

    assert payload.message is not None
    return service.continue_session(payload.sessionId, payload.message)
