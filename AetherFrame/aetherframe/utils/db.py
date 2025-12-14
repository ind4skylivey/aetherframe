"""Database session helpers."""

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_settings


def _build_db_url() -> str:
    s = get_settings()
    if s.db_url:
        return s.db_url
    return (
        f"postgresql+psycopg://{s.postgres_user}:{s.postgres_password}"
        f"@{s.postgres_host}:{s.postgres_port}/{s.postgres_db}"
    )


def get_engine():
    return create_engine(_build_db_url(), future=True)


def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session, future=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency to provide a scoped session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
