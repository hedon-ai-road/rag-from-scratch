"""
Database models and configuration.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from models.base import Base
from models.document import Document, DocumentChunk
import constants

# Database configuration
DATABASE_URL = f"sqlite:///{constants.DATA_DIR}/rag.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # For SQLite
    echo=False,  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables in the database."""
    # Ensure data directory exists
    constants.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session() -> Session:
    """Get database session context manager."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """Get database session (for dependency injection)."""
    return SessionLocal()
