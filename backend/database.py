"""
Database engine and session management for Online Quiz System using SQLAlchemy 2.0.

Enforces:
- Foreign key constraints (PRAGMA foreign_keys = ON for SQLite, native FKs in PostgreSQL)
- Relational constraints and foreign keys at the database storage level
- Connection pooling and session lifecycle management
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import DATABASE_URL
from backend.db_models import Base

# Engine configuration
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine: Engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# Enable Foreign Key checks on SQLite (SQLite turns FK checks off by default)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine: Engine | None = None) -> None:
    """
    Initialize all database tables with normalized schemas, indexes, and integrity constraints.
    Initializes all database tables.
    """
    eng = target_engine if target_engine is not None else engine
    Base.metadata.create_all(bind=eng)


if __name__ == "__main__":
    init_db()
    print("Database schema successfully created using engine:", engine.url)
