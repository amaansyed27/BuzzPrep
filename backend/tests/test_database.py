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
