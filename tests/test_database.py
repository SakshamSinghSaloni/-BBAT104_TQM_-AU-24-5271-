"""
Test suite for database layer and Q06 Feature 1: Unique ID Constraints.
"""

import pytest
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.database import init_db
from backend.db_models import Participant, Question, Quiz, Session as QuizSession, User


@pytest.fixture
def test_db(tmp_path):
    """Fixture providing an isolated SQLite database session for each test run."""
    db_file = tmp_path / "test_quiz.db"
    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    init_db(test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_tables_created_successfully(test_db: Session):
    """Verify that all core tables exist after initialization."""
    inspector = inspect(test_db.bind)
    tables = set(inspector.get_table_names())
    assert {"users", "quizzes", "questions", "sessions", "participants", "submissions"}.issubset(tables)


def test_foreign_key_cascade_deletion(test_db: Session):
    """Verify that deleting a quiz cascades to its associated questions."""
    quiz = Quiz(
        title="Test Quiz",
        description="Desc",
        created_at="2026-10-11T10:00:00",
        updated_at="2026-10-11T10:00:00",
    )
    test_db.add(quiz)
    test_db.commit()

    question = Question(
        quiz_id=quiz.id,
        question_text="Sample Question?",
        question_type="mcq",
        correct_answer="Answer A",
        created_at="2026-10-11T10:00:00",
    )
    test_db.add(question)
    test_db.commit()

    # Confirm question is saved
    count_before = test_db.query(Question).filter(Question.quiz_id == quiz.id).count()
    assert count_before == 1

    # Delete parent quiz
    test_db.delete(quiz)
    test_db.commit()

    # Questions referencing this quiz must be automatically deleted by cascade
    count_after = test_db.query(Question).filter(Question.quiz_id == quiz.id).count()
    assert count_after == 0


def test_q06_unique_session_code_constraint(test_db: Session):
    """FR-Q1: Verify UNIQUE constraint on session_code rejects duplicates."""
    quiz = Quiz(
        title="Quiz 1",
        created_at="2026-10-11T10:00:00",
        updated_at="2026-10-11T10:00:00",
    )
    test_db.add(quiz)
    test_db.commit()

    sess1 = QuizSession(
        quiz_id=quiz.id,
        session_code="CODE123",
        started_at="2026-10-11T10:00:00",
    )
    test_db.add(sess1)
    test_db.commit()

    # Attempting to insert identical session_code must raise IntegrityError
    sess2 = QuizSession(
        quiz_id=quiz.id,
        session_code="CODE123",
        started_at="2026-10-11T10:05:00",
    )
    test_db.add(sess2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_q06_unique_participant_per_session_constraint(test_db: Session):
    """FR-Q1: Verify UNIQUE(session_id, student_identifier) prevents duplicate join."""
    quiz = Quiz(
        title="Quiz 1",
        created_at="2026-10-11T10:00:00",
        updated_at="2026-10-11T10:00:00",
    )
    test_db.add(quiz)
    test_db.commit()

    sess = QuizSession(
        quiz_id=quiz.id,
        session_code="CODE999",
        started_at="2026-10-11T10:00:00",
    )
    test_db.add(sess)
    test_db.commit()

    p1 = Participant(
        session_id=sess.id,
        student_name="Alice",
        student_identifier="AU-24-0001",
        joined_at="2026-10-11T10:01:00",
    )
    test_db.add(p1)
    test_db.commit()

    # Same student joining the same session again must be rejected
    p2 = Participant(
        session_id=sess.id,
        student_name="Alice Duplicate",
        student_identifier="AU-24-0001",
        joined_at="2026-10-11T10:02:00",
    )
    test_db.add(p2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_user_repository_update_profile_and_password(test_db: Session):
    """Verify UserRepository can update profile display name and password hash."""
    from backend.repositories.user_repo import UserRepository

    repo = UserRepository(test_db)
    user = repo.create(
        email="prof.test@example.edu",
        password_hash="hash_old",
        name="Prof. Original Name",
        role="teacher",
    )
    assert user.id is not None
    assert user.name == "Prof. Original Name"

    # 1. Update Profile (Name)
    updated = repo.update_profile(user.id, "  Prof. Updated Name  ")
    assert updated is not None
    assert updated.name == "Prof. Updated Name"

    # 2. Update Password Hash
    updated_pwd = repo.update_password(user.id, "hash_new_secure")
    assert updated_pwd is not None
    assert updated_pwd.password_hash == "hash_new_secure"

    # 3. Nonexistent user returns None
    assert repo.update_profile(999999, "Ghost") is None
    assert repo.update_password(999999, "GhostHash") is None
