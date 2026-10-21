"""
Database connection management and schema initialization for Online Quiz System.

Enforces:
- Foreign key constraints (PRAGMA foreign_keys = ON)
- Q06 Feature 1: Unique ID Constraints at the database storage level
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Generator

# Default database file path (located in the backend directory)
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "quiz_system.db"


def get_db_path() -> Path:
    """Return the database path, allowing override via environment variable."""
    override = os.getenv("QUIZ_DB_PATH")
    if override:
        return Path(override)
    return DEFAULT_DB_PATH


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """
    Create and return an SQLite connection with Row factory and foreign keys enabled.
    """
    path = db_path if db_path is not None else get_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    # Crucial for data integrity: SQLite turns FK checks off by default
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency for obtaining a database connection per request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path | str | None = None) -> None:
    """
    Initialize all database tables with normalized schemas, indexes, and integrity constraints.
    Enforces Q06 Feature 1: Unique ID Constraints.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()

        # 1. Quizzes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        # 2. Questions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL DEFAULT 'mcq',
                options_json TEXT,
                correct_answer TEXT NOT NULL,
                points INTEGER NOT NULL DEFAULT 1,
                order_index INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
                CONSTRAINT uq_quiz_question_text UNIQUE (quiz_id, question_text)
            );
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_questions_quiz_id
            ON questions(quiz_id);
            """
        )

        # 3. Sessions table (Q06: UNIQUE session_code)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                session_code TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active',
                started_at TEXT NOT NULL,
                ended_at TEXT,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            );
            """
        )

        # 4. Participants table (Q06: UNIQUE participant per session)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                student_identifier TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                CONSTRAINT uq_session_participant UNIQUE (session_id, student_identifier)
            );
            """
        )

        # 5. Submissions table (Q06: UNIQUE submission per question per participant)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                is_correct INTEGER,
                points_awarded INTEGER NOT NULL DEFAULT 0,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (participant_id) REFERENCES participants(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                CONSTRAINT uq_participant_question UNIQUE (participant_id, question_id)
            );
            """
        )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", get_db_path())
