from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.interview import Base

DEFAULT_DATABASE_URL = "sqlite:///./buzzprep.db"


def resolve_database_url(database_url: str | None = None) -> str:
    """Resolve the configured database URL and normalize PostgreSQL for psycopg 3."""
    url = database_url or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL

    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Database:
    """Owns the SQLAlchemy engine and creates short-lived unit-of-work sessions."""

    def __init__(self, database_url: str | None = None) -> None:
        self.url = resolve_database_url(database_url)
        connect_args = {"check_same_thread": False} if self.url.startswith("sqlite") else {}
        self.engine: Engine = create_engine(
            self.url,
            connect_args=connect_args,
            pool_pre_ping=not self.url.startswith("sqlite"),
        )
        self._session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

    def create_all(self) -> None:
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            yield session

    def dispose(self) -> None:
        self.engine.dispose()
