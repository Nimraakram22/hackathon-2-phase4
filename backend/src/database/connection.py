"""
Database connection module for Neon PostgreSQL.

This module provides database connection and session management using SQLModel.
"""

from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel

from ..config import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def create_db_and_tables() -> None:
    """
    Create all database tables.

    This should only be used in development. In production, use Alembic migrations.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.

    Yields:
        Session: SQLAlchemy session

    Example:
        ```python
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            users = session.query(User).all()
            return users
        ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Get a database session as a context manager.

    Yields:
        Session: SQLAlchemy session

    Example:
        ```python
        with get_session_context() as session:
            user = session.query(User).first()
        ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
