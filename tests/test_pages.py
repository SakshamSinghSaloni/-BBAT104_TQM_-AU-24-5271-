"""
Integration test suite for Server-Side Rendered (SSR) HTML Web Pages.
Verifies page availability, layout rendering, unauthenticated redirect protection, and student workflows.
"""

import pytest


def test_public_pages_render(client):
    """Verify that public landing and entry pages return HTTP 200."""
    routes = ["/", "/join", "/auth/login", "/auth/register"]
    for route in routes:
        resp = client.get(route)
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


def test_protected_pages_redirect_unauthenticated(client):
    """Verify that visiting protected instructor views redirects unauthenticated guests to login."""
    protected_routes = ["/dashboard", "/quizzes", "/quizzes/1/questions", "/sessions/1/results"]
    for route in protected_routes:
        resp = client.get(route, follow_redirects=False)
        assert resp.status_code == 303
        assert resp.headers["location"] == "/auth/login"


def test_dashboard_renders_for_authenticated_teacher(auth_client):
    """Verify that an authenticated instructor can view the dashboard."""
    resp = auth_client.get("/dashboard")
    assert resp.status_code == 200
    assert "Instructor Dashboard" in resp.text
    assert "Live & Recent Assessment Sessions" in resp.text


def test_quizzes_page_renders_for_authenticated_teacher(auth_client):
    """Verify that an authenticated instructor can view the Quiz Library."""
    resp = auth_client.get("/quizzes")
    assert resp.status_code == 200
    assert "Quiz Library" in resp.text
    assert "Create New Quiz" in resp.text


def test_student_web_flow(client, auth_client):
    """End-to-end test of the student web interface: Join -> Take Quiz -> Submit -> View Results."""
    # 1. Instructor creates quiz with 1 question & launches session
    q_resp = auth_client.post("/api/quizzes", json={"title": "Web Flow Midterm"})
    quiz_id = q_resp.json()["id"]

    auth_client.post(
        f"/api/quizzes/{quiz_id}/questions",
        json={
            "question_text": "What protocol is used on the World Wide Web?",
            "question_type": "mcq",
            "options": ["HTTP", "FTP", "SMTP", "SSH"],
            "correct_answer": "HTTP",
            "points": 1,
        },
    )

    sess = auth_client.post("/api/sessions", json={"quiz_id": quiz_id}).json()
    code = sess["session_code"]

    # 2. Student joins via HTML form POST
    join_form_resp = client.post(
        "/join",
        data={
            "session_code": code,
            "student_name": "Robin Hood",
            "student_identifier": "STU-777",
        },
        follow_redirects=False,
    )
    assert join_form_resp.status_code == 303
    redirect_take_url = join_form_resp.headers["location"]
    assert f"/session/{code}/take?participant_id=" in redirect_take_url

    # 3. Student renders the take quiz page
    take_page_resp = client.get(redirect_take_url)
    assert take_page_resp.status_code == 200
    assert "Robin Hood" in take_page_resp.text
    assert "What protocol is used on the World Wide Web?" in take_page_resp.text

    # Extract participant_id from redirect URL
    participant_id = redirect_take_url.split("participant_id=")[-1]

    # 4. Fetch questions to find q_id
    q_items = client.get(f"/api/sessions/{code}/questions").json()
    q_id = q_items[0]["id"]

    # 5. Student submits answers via HTML form POST
    submit_form_resp = client.post(
        f"/session/{code}/submit",
        data={"participant_id": participant_id, f"q_{q_id}": "HTTP"},
        follow_redirects=False,
    )
    assert submit_form_resp.status_code == 303
    redirect_results_url = submit_form_resp.headers["location"]
    assert f"/session/{code}/results?participant_id={participant_id}" == redirect_results_url

    # 6. Student views scorecard
    results_page_resp = client.get(redirect_results_url)
    assert results_page_resp.status_code == 200
    assert "Evaluation Complete" in results_page_resp.text
    assert "100.0%" in results_page_resp.text


def test_create_quiz_web_form(auth_client):
    """Verify TC-MAN-04 and TC-MAN-05 web form quiz creation and duplicate rejection."""
    # 1. Successful quiz creation
    resp = auth_client.post(
        "/quizzes",
        data={"title": "Computer Architecture Fundamentals", "description": "CPU and memory."},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/quizzes"

    # Verify quiz renders in list
    list_resp = auth_client.get("/quizzes")
    assert "Computer Architecture Fundamentals" in list_resp.text

    # 2. Duplicate quiz creation rejected
    dup_resp = auth_client.post(
        "/quizzes",
        data={"title": "Computer Architecture Fundamentals", "description": "Duplicate attempt."},
        follow_redirects=False,
    )
    assert dup_resp.status_code == 400
    assert "already exists" in dup_resp.text


def test_add_question_web_form(auth_client):
    """Verify TC-MAN-06 web form question authoring and questions view."""
    # 1. Create parent quiz
    resp = auth_client.post(
        "/quizzes",
        data={"title": "Data Structures Final", "description": "Stacks and Queues."},
        follow_redirects=False,
    )
    assert resp.status_code == 303

    # Find quiz id from page
    list_resp = auth_client.get("/quizzes")
    assert "Data Structures Final" in list_resp.text

    # Get questions page
    q_page_resp = auth_client.get("/quizzes/1/questions")
    assert q_page_resp.status_code == 200

    # Add question via HTML form
    add_resp = auth_client.post(
        "/quizzes/1/questions",
        data={
            "question_text": "What is FIFO data structure?",
            "question_type": "mcq",
            "points": 2,
            "mcq_correct_idx": 1,
            "mcq_option_1": "Queue",
            "mcq_option_2": "Stack",
            "mcq_option_3": "Tree",
            "mcq_option_4": "Graph",
        },
        follow_redirects=False,
    )
    assert add_resp.status_code == 303
    assert add_resp.headers["location"] == "/quizzes/1/questions"

    # Verify question renders on questions page
    updated_q_page = auth_client.get("/quizzes/1/questions")
    assert updated_q_page.status_code == 200
    assert "What is FIFO data structure?" in updated_q_page.text

    # Add True/False question
    tf_resp = auth_client.post(
        "/quizzes/1/questions",
        data={
            "question_text": "L1 cache is faster than main memory RAM.",
            "question_type": "true_false",
            "points": 1,
            "tf_answer": "True",
        },
        follow_redirects=False,
    )
    assert tf_resp.status_code == 303
    assert tf_resp.headers["location"] == "/quizzes/1/questions"

    # Add Short Answer question
    sa_resp = auth_client.post(
        "/quizzes/1/questions",
        data={
            "question_text": "Name the memory unit holding currently executing instructions.",
            "question_type": "short_answer",
            "points": 3,
            "short_answer_text": "Instruction Register",
        },
        follow_redirects=False,
    )
    assert sa_resp.status_code == 303
    assert sa_resp.headers["location"] == "/quizzes/1/questions"

    # Verify all 3 questions render with their types and answers
    final_page = auth_client.get("/quizzes/1/questions")
    assert final_page.status_code == 200
    assert "L1 cache is faster than main memory RAM." in final_page.text
    assert "TRUE_FALSE" in final_page.text
    assert "Name the memory unit holding currently executing instructions." in final_page.text
    assert "SHORT_ANSWER" in final_page.text
    assert "Instruction Register" in final_page.text
