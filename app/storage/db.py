from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
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
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


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
