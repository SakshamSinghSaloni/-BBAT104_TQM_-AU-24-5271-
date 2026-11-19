"""
Integration test suite for Quiz Sessions, Student Join, Auto-Grading, and Results Analytics.
Verifies collision-free session codes, duplicate participant prevention, duplicate submission prevention, and scoring.
"""

import pytest


@pytest.fixture
def sample_quiz_with_questions(auth_client):
    """Creates a sample quiz with 3 diverse questions (MCQ, True/False, Short Answer)."""
    # 1. Create Quiz
    quiz_resp = auth_client.post(
        "/api/quizzes",
        json={"title": "Data Structures Evaluation", "description": "Core concepts test"},
    )
    assert quiz_resp.status_code == 201
    quiz_id = quiz_resp.json()["id"]

    # 2. Add MCQ
    auth_client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "What is the worst-case time complexity of quicksort?",
            "question_type": "mcq",
            "options": ["O(n log n)", "O(n^2)", "O(n)", "O(1)"],
            "correct_answer": "O(n^2)",
            "points": 2,
            "order_index": 1,
        },
    )

    # 3. Add True/False
    auth_client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "A queue operates on a First-In-First-Out (FIFO) basis.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "points": 1,
            "order_index": 2,
        },
    )

    # 4. Add Short Answer
    auth_client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "Name the data structure primarily used to implement recursion.",
            "question_type": "short_answer",
            "correct_answer": "Stack",
            "points": 2,
            "order_index": 3,
        },
    )

    return quiz_id


def test_create_session_success(auth_client, sample_quiz_with_questions):
    """Verify that launching a session returns 201 with a unique 6-character code."""
    quiz_id = sample_quiz_with_questions
    resp = auth_client.post("/api/sessions", json={"quiz_id": quiz_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["quiz_id"] == quiz_id
    assert data["status"] == "active"
    assert len(data["session_code"]) == 6
    assert data["participant_count"] == 0


def test_create_session_quiz_not_found(auth_client):
    """Verify that launching a session for a nonexistent quiz returns 404."""
    resp = auth_client.post("/api/sessions", json={"quiz_id": 9999})
    assert resp.status_code == 404


def test_student_join_session_success(client, auth_client, sample_quiz_with_questions):
    """Verify that a student can join an active session with Name + Student ID."""
    quiz_id = sample_quiz_with_questions
    sess_resp = auth_client.post("/api/sessions", json={"quiz_id": quiz_id})
    session_code = sess_resp.json()["session_code"]

    # Student joins (unauthenticated client)
    join_resp = client.post(
        f"/api/sessions/{session_code}/join",
        json={"student_name": "Alex Morgan", "student_identifier": "CS-101"},
    )
    assert join_resp.status_code == 201
    data = join_resp.json()
    assert data["student_name"] == "Alex Morgan"
    assert data["student_identifier"] == "CS-101"
    assert "id" in data


def test_student_join_duplicate_rejected(client, auth_client, sample_quiz_with_questions):
    """Verify that joining with the same Student ID in the same session is rejected with 409."""
    quiz_id = sample_quiz_with_questions
    sess_resp = auth_client.post("/api/sessions", json={"quiz_id": quiz_id})
    session_code = sess_resp.json()["session_code"]

    payload = {"student_name": "Alex Morgan", "student_identifier": "CS-101"}
    first_resp = client.post(f"/api/sessions/{session_code}/join", json=payload)
    assert first_resp.status_code == 201

    # Duplicate attempt
    dup_resp = client.post(f"/api/sessions/{session_code}/join", json=payload)
    assert dup_resp.status_code == 409
    assert "already joined" in dup_resp.json()["detail"]


def test_student_join_different_session_allowed(client, auth_client, sample_quiz_with_questions):
    """Verify that the same Student ID CAN join two different assessment sessions."""
    quiz_id = sample_quiz_with_questions
    sess1 = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()["session_code"]
    sess2 = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()["session_code"]

    payload = {"student_name": "Taylor Swift", "student_identifier": "STU-555"}
    resp1 = client.post(f"/api/sessions/{sess1}/join", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post(f"/api/sessions/{sess2}/join", json=payload)
    assert resp2.status_code == 201


def test_student_join_ended_session_rejected(client, auth_client, sample_quiz_with_questions):
    """Verify that joining an ended session returns 400 Bad Request."""
    quiz_id = sample_quiz_with_questions
    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    session_id = sess["id"]
    session_code = sess["session_code"]

    # End the session
    end_resp = auth_client.post(f"/api/sessions/{session_id}/end")
    assert end_resp.status_code == 200

    # Try to join
    join_resp = client.post(
        f"/api/sessions/{session_code}/join",
        json={"student_name": "Late Student", "student_identifier": "LATE-01"},
    )
    assert join_resp.status_code == 400
    assert "ended" in join_resp.json()["detail"]


def test_get_session_questions_omits_answers(client, auth_client, sample_quiz_with_questions):
    """Verify that test items returned to students omit 'correct_answer' for exam security."""
    quiz_id = sample_quiz_with_questions
    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    session_code = sess["session_code"]

    resp = client.get(f"/api/sessions/{session_code}/questions")
    assert resp.status_code == 200
    questions = resp.json()
    assert len(questions) == 3

    for q in questions:
        assert "question_text" in q
        assert "question_type" in q
        assert "points" in q
        # correct_answer MUST NOT be leaked to client
        assert "correct_answer" not in q


def test_submit_answers_and_auto_grading(client, auth_client, sample_quiz_with_questions):
    """Verify that submitting answers automatically grades them and returns detailed feedback."""
    quiz_id = sample_quiz_with_questions
    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    session_code = sess["session_code"]

    # 1. Student joins
    part_resp = client.post(
        f"/api/sessions/{session_code}/join",
        json={"student_name": "Jordan Lee", "student_identifier": "CS-999"},
    )
    participant_id = part_resp.json()["id"]

    # 2. Fetch questions to get IDs
    questions = client.get(f"/api/sessions/{session_code}/questions").json()
    q_map = {q["question_type"]: q["id"] for q in questions}

    # 3. Submit answers: 2 correct, 1 wrong
    submission_payload = {
        "participant_id": participant_id,
        "answers": [
            {"question_id": q_map["mcq"], "answer_text": "O(n^2)"},            # Correct (+2)
            {"question_id": q_map["true_false"], "answer_text": "False"},        # Incorrect (0)
            {"question_id": q_map["short_answer"], "answer_text": "   stack   "}, # Correct (+2, case/trim)
        ],
    }

    sub_resp = client.post(f"/api/sessions/{session_code}/submit", json=submission_payload)
    assert sub_resp.status_code == 200
    result = sub_resp.json()

    assert result["participant_id"] == participant_id
    assert result["total_score"] == 4  # 2 + 0 + 2 = 4
    assert result["max_score"] == 5    # 2 + 1 + 2 = 5
    assert result["percentage"] == 80.0
    assert len(result["details"]) == 3


def test_duplicate_submission_rejected(client, auth_client, sample_quiz_with_questions):
    """Verify that submitting a quiz twice for the same participant returns 409 Conflict."""
    quiz_id = sample_quiz_with_questions
    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    session_code = sess["session_code"]

    part = client.post(
        f"/api/sessions/{session_code}/join",
        json={"student_name": "Sam Carter", "student_identifier": "CS-333"},
    ).json()

    questions = client.get(f"/api/sessions/{session_code}/questions").json()
    answers = [{"question_id": q["id"], "answer_text": "any answer"} for q in questions]

    payload = {"participant_id": part["id"], "answers": answers}

    # First submit
    sub1 = client.post(f"/api/sessions/{session_code}/submit", json=payload)
    assert sub1.status_code == 200

    # Second submit (duplicate attempt)
    sub2 = client.post(f"/api/sessions/{session_code}/submit", json=payload)
    assert sub2.status_code == 409
    assert "already submitted" in sub2.json()["detail"]


def test_session_results_analytics(client, auth_client, sample_quiz_with_questions):
    """Verify aggregated session analytics, leaderboard, and accuracy rates."""
    quiz_id = sample_quiz_with_questions
    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    session_id = sess["id"]
    session_code = sess["session_code"]

    # Student 1 joins & submits (all correct: 5/5)
    p1 = client.post(
        f"/api/sessions/{session_code}/join",
        json={"student_name": "Alice Top", "student_identifier": "TOP-1"},
    ).json()
    questions = client.get(f"/api/sessions/{session_code}/questions").json()
    q_map = {q["question_type"]: q["id"] for q in questions}

    client.post(
        f"/api/sessions/{session_code}/submit",
        json={
            "participant_id": p1["id"],
            "answers": [
                {"question_id": q_map["mcq"], "answer_text": "O(n^2)"},
                {"question_id": q_map["true_false"], "answer_text": "True"},
                {"question_id": q_map["short_answer"], "answer_text": "Stack"},
            ],
        },
    )

    # Fetch instructor results
    res_resp = auth_client.get(f"/api/sessions/{session_id}/results")
    assert res_resp.status_code == 200
    data = res_resp.json()

    assert data["session_id"] == session_id
    assert data["total_participants"] == 1
    assert data["total_submissions"] == 1
    assert data["highest_score"] == 5
    assert data["average_score"] == 5.0
    assert len(data["leaderboard"]) == 1
    assert data["leaderboard"][0]["student_name"] == "Alice Top"
    assert len(data["question_stats"]) == 3
