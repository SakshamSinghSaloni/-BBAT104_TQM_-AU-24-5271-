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


def test_api_q06_search_before_add_rejects_duplicate_quiz(client):
    """FR-Q3: API returns 409 Conflict when attempting to create duplicate quiz title."""
    payload = {"title": "Web Development", "description": "HTML & CSS"}
    resp1 = client.post("/api/quizzes", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/quizzes", json=payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"]


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


def test_api_q06_search_before_add_rejects_duplicate_question(client):
    """FR-Q3: API returns 409 Conflict when adding duplicate question to same quiz."""
    quiz_id = client.post("/api/quizzes", json={"title": "Discrete Math"}).json()["id"]

    q_payload = {
        "question_text": "Is the empty set a subset of every set?",
        "question_type": "true_false",
        "correct_answer": "True",
        "points": 1,
    }
    resp1 = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload)
    assert resp1.status_code == 201

    resp2 = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"]


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


def test_api_update_question(client):
    """FR-07: Update question modifications persist."""
    quiz_id = client.post("/api/quizzes", json={"title": "Update Q Test"}).json()["id"]
    q_payload = {
        "question_text": "Original text?",
        "question_type": "mcq",
        "options": ["A", "B", "C"],
        "correct_answer": "A",
        "points": 1,
    }
    q_id = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload).json()["id"]

    resp = client.put(f"/api/questions/{q_id}", json={"question_text": "Updated text?", "correct_answer": "B"})
    assert resp.status_code == 200
    assert resp.json()["question_text"] == "Updated text?"
    assert resp.json()["correct_answer"] == "B"


def test_api_delete_question(client):
    """FR-08: Delete question removes record."""
    quiz_id = client.post("/api/quizzes", json={"title": "Delete Q Test"}).json()["id"]
    q_payload = {
        "question_text": "To be deleted?",
        "question_type": "mcq",
        "options": ["X", "Y"],
        "correct_answer": "X",
    }
    q_id = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload).json()["id"]

    resp = client.delete(f"/api/questions/{q_id}")
    assert resp.status_code == 200

    assert client.get(f"/api/questions/{q_id}").status_code == 404


def test_api_update_question_rejects_answer_not_in_options(client):
    """FR-Q2: Update path validates answer is in options."""
    quiz_id = client.post("/api/quizzes", json={"title": "Validation Test"}).json()["id"]
    q_payload = {
        "question_text": "Pick one",
        "question_type": "mcq",
        "options": ["A", "B"],
        "correct_answer": "A",
    }
    q_id = client.post(f"/api/quizzes/{quiz_id}/questions", json=q_payload).json()["id"]

    resp = client.put(f"/api/questions/{q_id}", json={"correct_answer": "Z"})
    assert resp.status_code == 409
    assert "must be present in the options" in resp.json()["detail"]


def test_api_update_quiz_rejects_duplicate_title(client):
    """FR-Q3: Update path detects duplicate title."""
    client.post("/api/quizzes", json={"title": "Existing Quiz"})
    second = client.post("/api/quizzes", json={"title": "Another Quiz"}).json()

    resp = client.put(f"/api/quizzes/{second['id']}", json={"title": "Existing Quiz"})
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_api_update_question_rejects_duplicate_text(client):
    """FR-Q3: Update question rejects duplicate prompt in the same quiz."""
    quiz_id = client.post("/api/quizzes", json={"title": "Dup Q Test"}).json()["id"]
    client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={"question_text": "Q1 Text", "question_type": "mcq", "options": ["A", "B"], "correct_answer": "A"},
    )
    q2 = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={"question_text": "Q2 Text", "question_type": "mcq", "options": ["A", "B"], "correct_answer": "A"},
    ).json()

    resp = client.put(f"/api/questions/{q2['id']}", json={"question_text": "Q1 Text"})
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]
