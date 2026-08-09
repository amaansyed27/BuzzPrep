from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

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


def uses_transaction_pooler(database_url: str) -> bool:
    """Return whether the URL targets a transaction-pooling Postgres endpoint."""
    return database_url.startswith("postgresql+") and make_url(database_url).port == 6543


def database_engine_options(database_url: str) -> dict[str, object]:
    """Build engine options for SQLite, standard Postgres, or a transaction pooler."""
    is_sqlite = database_url.startswith("sqlite")
    is_transaction_pooler = uses_transaction_pooler(database_url)
    connect_args: dict[str, object]
    if is_sqlite:
        connect_args = {"check_same_thread": False}
    elif is_transaction_pooler:
        # Supavisor transaction mode swaps server connections between transactions.
        # Disable psycopg's automatic prepared statements for compatibility.
        connect_args = {"prepare_threshold": None}
    else:
        connect_args = {}

    engine_options: dict[str, object] = {
        "connect_args": connect_args,
        "pool_pre_ping": not is_sqlite,
    }
    if is_transaction_pooler:
        # The external transaction pooler already owns connection reuse. Avoid
        # multiplying open connections across serverless function instances.
        engine_options["poolclass"] = NullPool
    return engine_options


class Database:
    """Owns the SQLAlchemy engine and creates short-lived unit-of-work sessions."""

    def __init__(self, database_url: str | None = None) -> None:
        self.url = resolve_database_url(database_url)
        self.engine: Engine = create_engine(
            self.url,
            **database_engine_options(self.url),
        )
        self._session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

    def create_all(self) -> None:
        Base.metadata.create_all(self.engine)
        self._apply_compatible_schema_upgrades()

    def _apply_compatible_schema_upgrades(self) -> None:
        """Apply additive upgrades for databases created before current metadata."""
        with self.engine.begin() as connection:
            inspector = inspect(connection)
            if "interview_sessions" not in inspector.get_table_names():
                return
            columns = {column["name"] for column in inspector.get_columns("interview_sessions")}
            if "owner_id" not in columns:
                connection.execute(
                    text("ALTER TABLE interview_sessions ADD COLUMN owner_id VARCHAR(255)")
                )
            if "integrity_telemetry" not in columns:
                default_value = "'[]'::jsonb" if self.url.startswith("postgresql+") else "'[]'"
                connection.execute(
                    text(
                        "ALTER TABLE interview_sessions ADD COLUMN integrity_telemetry "
                        f"JSON NOT NULL DEFAULT {default_value}"
                    )
                )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_interview_sessions_owner_id "
                    "ON interview_sessions (owner_id)"
                )
            )

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            yield session

    def dispose(self) -> None:
        self.engine.dispose()
