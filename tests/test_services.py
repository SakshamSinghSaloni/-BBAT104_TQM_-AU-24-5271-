"""
Unit tests for Models (Q06 Pre-add Validation) and Services (Q06 Search Before Add).
"""

import pytest
from pydantic import ValidationError
from backend.database import get_connection, init_db
from backend.models import QuestionCreate, QuestionUpdate, QuizCreate
from backend.services.question_service import QuestionService
from backend.services.quiz_service import QuizService


@pytest.fixture
def service_db(tmp_path):
    """Provides clean isolated database for service tests."""
    db_file = tmp_path / "test_services.db"
    init_db(db_file)
    conn = get_connection(db_file)
    try:
        yield conn
    finally:
        conn.close()


# ========================================================
# Q06 FEATURE 2: PRE-ADD VALIDATION TESTS (Pydantic Models)
# ========================================================

def test_q06_pre_add_validation_quiz_empty_title():
    """FR-Q2: Rejects blank/whitespace title before reaching DB."""
    with pytest.raises(ValidationError) as exc:
        QuizCreate(title="   ")
    assert "cannot be empty" in str(exc.value)


def test_q06_pre_add_validation_quiz_valid_clean():
    """FR-Q2: Trims whitespace and accepts valid title."""
    quiz = QuizCreate(title="  Python Basics  ", description=" Intro ")
    assert quiz.title == "Python Basics"
    assert quiz.description == "Intro"


def test_q06_pre_add_validation_mcq_requires_options():
    """FR-Q2: MCQ must include options list."""
    with pytest.raises(ValidationError) as exc:
        QuestionCreate(
            question_text="What is 2+2?",
            question_type="mcq",
            options=None,
            correct_answer="4",
        )
    assert "Options list is required" in str(exc.value)


def test_q06_pre_add_validation_mcq_answer_must_be_in_options():
    """FR-Q2: Correct answer must be one of the declared options."""
    with pytest.raises(ValidationError) as exc:
        QuestionCreate(
            question_text="Select primary color",
            question_type="mcq",
            options=["Red", "Green", "Blue"],
            correct_answer="Yellow",
        )
    assert "must be present in the options" in str(exc.value)


def test_q06_pre_add_validation_question_update_empty():
    """FR-Q2: QuestionUpdate rejects whitespace/empty fields."""
    with pytest.raises(ValidationError) as exc:
        QuestionUpdate(question_text="   ")
    assert "cannot be empty" in str(exc.value)

    with pytest.raises(ValidationError) as exc2:
        QuestionUpdate(correct_answer="   ")
    assert "cannot be empty" in str(exc2.value)


# ========================================================
# Q06 FEATURE 3: SEARCH BEFORE ADD TESTS (Services Layer)
# ========================================================

def test_q06_search_before_add_quiz_duplicate_detection(service_db):
    """FR-Q3: Search detects matching title and blocks duplicate quiz creation."""
    service = QuizService(service_db)
    q1 = service.create_quiz(title="Database Systems", description="First")
    assert q1["id"] is not None

    # Adding another quiz with the identical title must be blocked with ValueError
    with pytest.raises(ValueError) as exc:
        service.create_quiz(title="Database Systems", description="Second")
    assert "already exists" in str(exc.value)


def test_q06_search_before_add_question_duplicate_in_quiz(service_db):
    """FR-Q3: Search identifies duplicate question in the same quiz and blocks creation."""
    quiz_svc = QuizService(service_db)
    q_svc = QuestionService(service_db)

    quiz = quiz_svc.create_quiz(title="Math 101")
    quiz_id = quiz["id"]

    item1 = q_svc.add_question(
        quiz_id=quiz_id,
        question_text="Is 5 a prime number?",
        question_type="mcq",
        options=["Yes", "No"],
        correct_answer="Yes",
    )
    assert item1["id"] is not None

    # Adding duplicate question in the same quiz must raise ValueError
    with pytest.raises(ValueError) as exc:
        q_svc.add_question(
            quiz_id=quiz_id,
            question_text="  Is 5 a prime number? ",
            question_type="mcq",
            options=["Yes", "No"],
            correct_answer="Yes",
        )
    assert "already exists" in str(exc.value)
