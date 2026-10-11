"""
Integration test suite for the REST API layer and Q06 features via FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from backend.database import get_connection, get_db, init_db
from backend.main import app


@pytest.fixture
def client(tmp_path):
    """Provides a TestClient using an isolated temporary database."""
    test_db_file = tmp_path / "api_test.db"
    init_db(test_db_file)

    def override_get_db():
        conn = get_connection(test_db_file)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ========================================================
# CRUD & Q06 TESTS: QUIZZES
# ========================================================

def test_api_create_quiz_success(client):
    """FR-01: Create quiz endpoint works with valid data."""
    payload = {"title": "Operating Systems", "description": "Processes & Memory"}
    resp = client.post("/api/quizzes", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["title"] == "Operating Systems"
    assert data["question_count"] == 0


def test_api_q06_pre_add_validation_rejects_empty_title(client):
    """FR-Q2: API returns 422 Unprocessable Entity for blank title."""
    payload = {"title": "   ", "description": "Invalid"}
    resp = client.post("/api/quizzes", json=payload)
    assert resp.status_code == 422


def test_api_list_quizzes(client):
    """FR-02: List quizzes returns all created quizzes."""
    client.post("/api/quizzes", json={"title": "Quiz A"})
    client.post("/api/quizzes", json={"title": "Quiz B"})

    resp = client.get("/api/quizzes")
    assert resp.status_code == 200
    quizzes = resp.json()
    assert len(quizzes) == 2


def test_api_update_quiz(client):
    """FR-03: Update quiz modifications persist."""
    created = client.post("/api/quizzes", json={"title": "Initial"}).json()
    quiz_id = created["id"]

    resp = client.put(f"/api/quizzes/{quiz_id}", json={"title": "Modified Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Modified Title"


def test_api_delete_quiz(client):
    """FR-04: Delete quiz removes record."""
    created = client.post("/api/quizzes", json={"title": "To Delete"}).json()
    quiz_id = created["id"]

    resp = client.delete(f"/api/quizzes/{quiz_id}")
    assert resp.status_code == 200

    # Confirm 404 on subsequent get
    assert client.get(f"/api/quizzes/{quiz_id}").status_code == 404


# ========================================================
# CRUD & Q06 TESTS: QUESTIONS
# ========================================================

def test_api_add_and_list_question(client):
    """FR-05 & FR-06: Add question to quiz and list it."""
    quiz_id = client.post("/api/quizzes", json={"title": "Data Structures"}).json()["id"]

    q_payload = {
        "question_text": "What is the time complexity of binary search?",
        "question_type": "mcq",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_answer": "O(log n)",
        "points": 2,
    }
    resp = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload)
    assert resp.status_code == 201
    question = resp.json()
    assert question["correct_answer"] == "O(log n)"
    assert question["points"] == 2

    # Check quiz now reports 1 question
    quiz_resp = client.get(f"/api/quizzes/{quiz_id}").json()
    assert quiz_resp["question_count"] == 1


def test_api_q06_pre_add_validation_question_options(client):
    """FR-Q2: API rejects question where answer is not among options."""
    quiz_id = client.post("/api/quizzes", json={"title": "Quiz Test"}).json()["id"]

    bad_payload = {
        "question_text": "What color is the sky?",
        "question_type": "mcq",
        "options": ["Red", "Green"],
        "correct_answer": "Blue",
    }
    resp = client.post(f"/api/quizzes/{quiz_id}/questions", json=bad_payload)
    assert resp.status_code == 422
