from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.auth import require_authenticated_user
from app.api.interview import get_interview_session_service
from app.schemas.interview import InterviewHistoryDetail, InterviewHistoryList
from app.services.session import InterviewSessionService

router = APIRouter(prefix="/api/me/interviews", tags=["history"])


@router.get("", response_model=InterviewHistoryList)
def list_interviews(
    request: Request,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewHistoryList:
    user = require_authenticated_user(request)
    return InterviewHistoryList(interviews=service.list_history(user.user_id))


@router.get("/{session_id}", response_model=InterviewHistoryDetail)
def get_interview(
    session_id: str,
    request: Request,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewHistoryDetail:
    user = require_authenticated_user(request)
    return service.get_history(user.user_id, session_id)
