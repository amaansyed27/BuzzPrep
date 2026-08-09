from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.history import router as history_router
from app.api.interview import router as interview_router
from app.auth.base import AuthError, AuthService
from app.auth.factory import build_auth_service
from app.config import configured_cors_origins, load_environment
from app.db.database import Database
from app.interview.engine import AdaptiveInterviewEngine
from app.llm.factory import build_llm_provider
from app.memory.base import MemoryService
from app.memory.factory import build_memory_service
from app.services.interviewer import InterviewEngine, InterviewEngineError
from app.services.session import InterviewSessionError

load_environment()


def _validation_details(exc: RequestValidationError) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for error in exc.errors():
        details.append(
            {
                "loc": [str(part) for part in error.get("loc", ())],
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "validation_error"),
            }
        )
    return details


def create_app(
    *,
    database_url: str | None = None,
    interview_engine: InterviewEngine | None = None,
    memory_service: MemoryService | None = None,
    auth_service: AuthService | None = None,
) -> FastAPI:
    database = Database(database_url)
    memory = memory_service or build_memory_service()
    engine = interview_engine or AdaptiveInterviewEngine(build_llm_provider(), memory)
    auth = auth_service or build_auth_service()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.create_all()
        yield
        database.dispose()

    application = FastAPI(title="BuzzPrep API", version="0.3.0", lifespan=lifespan)
    application.state.database = database
    application.state.interview_engine = engine
    application.state.memory_service = memory
    application.state.auth_service = auth

    application.add_middleware(
        CORSMiddleware,
        allow_origins=configured_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_request",
                    "message": "Malformed interview request",
                    "details": _validation_details(exc),
                }
            },
        )

    @application.exception_handler(InterviewSessionError)
    async def interview_session_error_handler(
        request: Request, exc: InterviewSessionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @application.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @application.exception_handler(InterviewEngineError)
    async def interview_engine_error_handler(
        request: Request, exc: InterviewEngineError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "buzzprep-api"}

    application.include_router(interview_router)
    application.include_router(history_router)
    return application


app = create_app()
