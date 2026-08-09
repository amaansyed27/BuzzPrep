from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool, QueuePool

from app.db.database import (
    Database,
    database_engine_options,
    resolve_database_url,
    uses_transaction_pooler,
)


def test_resolve_database_url_uses_psycopg_driver() -> None:
    assert (
        resolve_database_url("postgresql://user:password@db.example.com:5432/app")
        == "postgresql+psycopg://user:password@db.example.com:5432/app"
    )


def test_transaction_pooler_uses_null_pool_and_disables_prepared_statements() -> None:
    database = Database(
        "postgresql://user:password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    )

    assert uses_transaction_pooler(database.url)
    assert isinstance(database.engine.pool, NullPool)
    assert database.engine.url.render_as_string(hide_password=True).endswith(
        "@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    )

    options = database_engine_options(database.url)
    assert options["connect_args"] == {"prepare_threshold": None}
    assert options["poolclass"] is NullPool


def test_standard_postgres_keeps_sqlalchemy_pool() -> None:
    database = Database("postgresql://user:password@db.example.com:5432/app")

    assert not uses_transaction_pooler(database.url)
    assert isinstance(database.engine.pool, QueuePool)


def test_create_all_adds_owner_column_to_legacy_database(tmp_path) -> None:
    database_path = tmp_path / "legacy.db"
    url = f"sqlite:///{database_path}"
    legacy_engine = create_engine(url)
    with legacy_engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE interview_sessions ("
            "id INTEGER PRIMARY KEY, session_id VARCHAR(255) NOT NULL UNIQUE, "
            "candidate_data JSON NOT NULL)"
        )
    legacy_engine.dispose()

    database = Database(url)
    try:
        database.create_all()
        columns = {column["name"] for column in inspect(database.engine).get_columns("interview_sessions")}
        indexes = {index["name"] for index in inspect(database.engine).get_indexes("interview_sessions")}
    finally:
        database.dispose()

    assert "owner_id" in columns
    assert "ix_interview_sessions_owner_id" in indexes
