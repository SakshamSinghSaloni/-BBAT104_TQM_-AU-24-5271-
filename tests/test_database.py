"""
Test suite for database layer and Q06 Feature 1: Unique ID Constraints.
"""

import sqlite3
import pytest
from backend.database import get_connection, init_db


@pytest.fixture
def test_db(tmp_path):
    """Fixture providing an isolated SQLite database for each test run."""
    db_file = tmp_path / "test_quiz.db"
    init_db(db_file)
    conn = get_connection(db_file)
    try:
        yield conn
    finally:
        conn.close()


def test_tables_created_successfully(test_db):
    """Verify that all 5 core tables exist after initialization."""
    cursor = test_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in cursor.fetchall()}
    assert {"quizzes", "questions", "sessions", "participants", "submissions"}.issubset(tables)


def test_foreign_key_cascade_deletion(test_db):
    """Verify that deleting a quiz cascades to its associated questions."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO quizzes (title, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Test Quiz", "Desc", "2026-10-11T10:00:00", "2026-10-11T10:00:00"),
    )
    quiz_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO questions (quiz_id, question_text, question_type, correct_answer, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (quiz_id, "Sample Question?", "mcq", "Answer A", "2026-10-11T10:00:00"),
    )
    test_db.commit()

    # Confirm question is saved
    cursor.execute("SELECT COUNT(*) as count FROM questions WHERE quiz_id = ?", (quiz_id,))
    assert cursor.fetchone()["count"] == 1

    # Delete the parent quiz
    cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    test_db.commit()

    # Questions referencing this quiz must be automatically deleted by cascade
    cursor.execute("SELECT COUNT(*) as count FROM questions WHERE quiz_id = ?", (quiz_id,))
    assert cursor.fetchone()["count"] == 0


def test_q06_unique_session_code_constraint(test_db):
    """FR-Q1: Verify UNIQUE constraint on session_code rejects duplicates."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO quizzes (title, created_at, updated_at) VALUES (?, ?, ?)",
        ("Quiz 1", "2026-10-11T10:00:00", "2026-10-11T10:00:00"),
    )
    quiz_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO sessions (quiz_id, session_code, started_at) VALUES (?, ?, ?)",
        (quiz_id, "CODE123", "2026-10-11T10:00:00"),
    )
    test_db.commit()

    # Attempting to insert identical session_code must raise IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO sessions (quiz_id, session_code, started_at) VALUES (?, ?, ?)",
            (quiz_id, "CODE123", "2026-10-11T10:05:00"),
        )
        test_db.commit()


def test_q06_unique_participant_per_session_constraint(test_db):
    """FR-Q1: Verify UNIQUE(session_id, student_identifier) prevents duplicate join."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO quizzes (title, created_at, updated_at) VALUES (?, ?, ?)",
        ("Quiz 1", "2026-10-11T10:00:00", "2026-10-11T10:00:00"),
    )
    quiz_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO sessions (quiz_id, session_code, started_at) VALUES (?, ?, ?)",
        (quiz_id, "CODE999", "2026-10-11T10:00:00"),
    )
    session_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO participants (session_id, student_name, student_identifier, joined_at) VALUES (?, ?, ?, ?)",
        (session_id, "Alice", "AU-24-0001", "2026-10-11T10:01:00"),
    )
    test_db.commit()

    # Same student joining the same session again must be rejected
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO participants (session_id, student_name, student_identifier, joined_at) VALUES (?, ?, ?, ?)",
            (session_id, "Alice Duplicate", "AU-24-0001", "2026-10-11T10:02:00"),
        )
        test_db.commit()
