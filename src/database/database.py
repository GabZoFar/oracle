"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from contextlib import contextmanager
from typing import Generator

from ..config import settings
from .models import Base


# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db_session() -> Generator[SQLSession, None, None]:
    """
    Get a database session with automatic cleanup.
    
    Usage:
        with get_db_session() as db:
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> SQLSession:
    """
    Get a database session (for dependency injection).
    Remember to close the session when done.
    """
    return SessionLocal()


def init_database() -> None:
    """Initialize the database by creating tables and ensuring directories exist."""
    settings.ensure_directories()
    create_tables() 