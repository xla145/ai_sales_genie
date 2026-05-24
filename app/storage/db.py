from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class DatabaseConfigError(RuntimeError):
    pass


def _sqlite_fallback_url(base_dir: Path) -> str:
    return f"sqlite+pysqlite:///{(base_dir / 'data' / 'hermes.db').resolve()}"


def get_database_url(base_dir: Path) -> str:
    configured = os.environ.get("DATABASE_URL")
    if configured:
        return configured

    mysql_host = os.environ.get("MYSQL_HOST")
    mysql_port = os.environ.get("MYSQL_PORT", "3306")
    mysql_user = os.environ.get("MYSQL_USER")
    mysql_password = os.environ.get("MYSQL_PASSWORD")
    mysql_database = os.environ.get("MYSQL_DATABASE")

    if mysql_host and mysql_user and mysql_database:
        password = mysql_password or ""
        return f"mysql+pymysql://{mysql_user}:{password}@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"

    return _sqlite_fallback_url(base_dir)


def build_engine(base_dir: Path) -> Engine:
    database_url = get_database_url(base_dir)
    if database_url.startswith("mysql+aiomysql://"):
        database_url = database_url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


def ensure_audit_user_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    audited_tables = {
        "projects",
        "requirement_analyses",
        "requirement_scenarios",
        "requirement_risks",
        "requirement_pending_items",
        "project_attachments",
        "project_sessions",
        "project_runs",
        "workflows",
    }

    dialect = engine.dialect.name
    with engine.begin() as connection:
        for table_name in sorted(audited_tables & table_names):
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name in ("created_id", "update_id"):
                if column_name not in columns:
                    if dialect == "sqlite":
                        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(32)"))
                    else:
                        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(32) NULL"))

        if "project_attachments" in table_names:
            columns = {column["name"] for column in inspector.get_columns("project_attachments")}
            attachment_columns = {
                "size": "INTEGER",
                "content_type": "VARCHAR(255)",
                "uploaded_at": "DATETIME",
            }
            for column_name, column_type in attachment_columns.items():
                if column_name not in columns:
                    connection.execute(text(f"ALTER TABLE project_attachments ADD COLUMN {column_name} {column_type} NULL"))


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
